#!/usr/bin/env python3
"""
Build script — generates two AEM content packages from content-package/

  b2b-ue-template-{VERSION}.zip
      Template-only package. Installs the Quick Site Creation template at
      /conf/global/site-templates/b2b-ue-1.0.0/.  Developer then creates the
      site manually via Sites → Create → Site from Template.

  b2b-ue-site-{VERSION}.zip
      Full-install package. Installs the template + page content + DAM.
      /conf/b2b-ue is intentionally excluded — that conf is owned by Quick
      Site Creation and stores the franklin.delivery GitHub proxy config that
      serves component-*.json to Universal Editor. Touching it causes 404s.
      Use merge mode for /content/b2b-ue to preserve site-level properties.

Usage:
    python3 build-packages.py           # builds both, version from VERSION below
    python3 build-packages.py --version 1.2.0
    python3 build-packages.py --template-only
    python3 build-packages.py --site-only

Source of truth:
    content-package/                    # package source (edit this)
      jcr_root/conf/global/site-templates/b2b-ue-1.0.0/
        site.zip                        # inner package — rebuild with the
                                        # Python rebuild scripts when page
                                        # content changes (see README.md)
      META-INF/vault/
        config.xml                      # shared vault config, copied into both
        filter.xml                      # used only for template package
        properties.xml                  # used only for template package
"""

import argparse
import io
import os
import zipfile

CONTENT_PKG_DIR = "content-package"
SITE_ZIP_REL = "jcr_root/conf/global/site-templates/b2b-ue-1.0.0/site.zip"

# Prefixes inside site.zip to exclude when embedding in any output package.
# - META-INF: rebuilt per package
# - CF models: dam:AssetModel node type may not exist on all AEM Cloud instances;
#   if present during QSC or direct install, the error causes a full rollback
#   and the site content never gets created.
SITE_ZIP_SKIP_PREFIXES = (
    "META-INF",
    "jcr_root/conf/b2b-ue/settings/dam/cfm/models",
)

DEFAULT_VERSION = "1.0.0"


def _read_src(rel_path: str) -> bytes:
    full = os.path.join(CONTENT_PKG_DIR, rel_path)
    with open(full, "rb") as f:
        return f.read()


def _cleaned_site_zip_bytes() -> bytes:
    """
    Return a cleaned site.zip with CF model nodes removed.

    The original site.zip includes /conf/b2b-ue/settings/dam/cfm/models/ which
    requires the dam:AssetModel JCR node type.  If that type is missing, the
    package manager raises an error and rolls back the ENTIRE site.zip install,
    leaving the site with no content pages.  Removing those nodes prevents the
    rollback so QSC (and direct installs) create the content successfully.
    """
    src_path = os.path.join(CONTENT_PKG_DIR, SITE_ZIP_REL)
    buf = io.BytesIO()
    skipped = 0
    with zipfile.ZipFile(src_path, "r") as src, \
         zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            if any(item.filename.startswith(p) for p in SITE_ZIP_SKIP_PREFIXES):
                skipped += 1
                continue
            dst.writestr(item.filename, src.read(item.filename))
        # Copy META-INF as-is (filter still covers /conf/b2b-ue so QSC writes
        # its cloud config there; we just don't ship broken CF model nodes)
        for item in src.infolist():
            if item.filename.startswith("META-INF"):
                dst.writestr(item.filename, src.read(item.filename))
    if skipped:
        print(f"    (cleaned site.zip: removed {skipped} CF model entries)")
    return buf.getvalue()


def build_template(version: str) -> str:
    """
    Template package — installs the Quick Site Creation template.
    When the developer runs Sites → Create → Site from Template, AEM installs
    the embedded site.zip which creates /content/b2b-ue with all pre-configured
    content (hero-b2b, solutions grid, etc.).

    The site.zip is rebuilt on-the-fly with CF model nodes removed so the QSC
    installation does not error and roll back the content pages.
    """
    out = f"b2b-ue-template-{version}.zip"
    if os.path.exists(out):
        os.remove(out)

    cleaned = _cleaned_site_zip_bytes()
    site_zip_arc = SITE_ZIP_REL  # arc path inside the outer zip

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(CONTENT_PKG_DIR):
            for fname in files:
                full = os.path.join(root, fname)
                arc = os.path.relpath(full, CONTENT_PKG_DIR)
                if arc == site_zip_arc:
                    # Replace with cleaned version
                    z.writestr(arc, cleaned)
                else:
                    z.write(full, arc)

    print(f"  [template]      {out}  ({os.path.getsize(out) // 1024} KB)")
    return out


def build_fullinstall(version: str) -> str:
    """
    Full-install package — template + all site content in one package.

    Filter modes:
      /conf/global/site-templates  → replace  (fixed, predictable structure)
      /content/b2b-ue              → merge    (preserves site-level properties
                                               set by Quick Site Creation)
      /content/dam/b2b-ue          → replace  (fully controlled asset set)

    /conf/b2b-ue is intentionally EXCLUDED from this package.
    That path is owned entirely by Quick Site Creation — it writes the GitHub
    repo cloud config that powers the franklin.delivery proxy (which serves
    component-*.json to Universal Editor). If we touch /conf/b2b-ue, we risk
    breaking the proxy and causing 404s for component-models/filters/definition.

    Workflow:
      1. First install: use b2b-ue-template + Quick Site Creation (sets up conf)
      2. Subsequent updates: reinstall b2b-ue-site (touches only content + DAM)
    """
    site_zip_path = os.path.join(CONTENT_PKG_DIR, SITE_ZIP_REL)
    if not os.path.exists(site_zip_path):
        raise FileNotFoundError(f"site.zip not found: {site_zip_path}")

    out = f"b2b-ue-site-{version}.zip"
    if os.path.exists(out):
        os.remove(out)

    filter_xml = """\
<?xml version="1.0" encoding="UTF-8"?>
<workspaceFilter version="1.0">
  <!-- Site template: replace is safe — fixed, predictable structure -->
  <filter root="/conf/global/site-templates/b2b-ue-1.0.0" mode="replace"/>
  <!-- Page content: merge — preserves site-level properties (cq:conf,
       sling:configRef, franklin.delivery proxy config etc.) that Quick Site
       Creation writes. Never use mode="replace" here. -->
  <filter root="/content/b2b-ue"/>
  <!-- DAM assets: replace — fully controlled by this package -->
  <filter root="/content/dam/b2b-ue" mode="replace"/>
  <!-- /conf/b2b-ue is intentionally omitted: owned by Quick Site Creation.
       Touching it breaks the franklin.delivery GitHub proxy that serves
       component-models.json / component-filters.json to Universal Editor. -->
</workspaceFilter>
"""

    properties_xml = f"""\
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
<properties>
  <entry key="name">b2b-ue-site</entry>
  <entry key="version">{version}</entry>
  <entry key="group">b2b-ue</entry>
  <entry key="description">B2B UE — Full site install (template + content). Merge-safe reinstall.</entry>
  <entry key="requiresRoot">false</entry>
  <entry key="packageType">content</entry>
</properties>
"""

    # full-install skips: META-INF (custom below) + conf/b2b-ue (owned by QSC)
    fullinstall_skip = (
        "META-INF",
        "jcr_root/conf/b2b-ue",
    )
    skipped = 0

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        # META-INF — custom filter + properties, shared vault config
        z.writestr("META-INF/vault/filter.xml", filter_xml)
        z.writestr("META-INF/vault/properties.xml", properties_xml)
        z.writestr("META-INF/vault/config.xml",
                   _read_src("META-INF/vault/config.xml").decode())

        # jcr_root from content-package/ (the site template tree)
        src_jcr = os.path.join(CONTENT_PKG_DIR, "jcr_root")
        for root, _, files in os.walk(src_jcr):
            for fname in files:
                full = os.path.join(root, fname)
                arc = os.path.relpath(full, CONTENT_PKG_DIR)
                z.write(full, arc)

        # jcr_root from site.zip (page content + DAM only — skip conf/b2b-ue)
        with zipfile.ZipFile(site_zip_path, "r") as site_z:
            for item in site_z.infolist():
                if any(item.filename.startswith(p) for p in fullinstall_skip):
                    skipped += 1
                    continue
                z.writestr(item.filename, site_z.read(item.filename))

    if skipped:
        print(f"  [full install]  skipped {skipped} entries (conf/b2b-ue + META-INF)")
    print(f"  [full install]  {out}  ({os.path.getsize(out) // 1024} KB)")
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Build AEM content packages for b2b-ue"
    )
    parser.add_argument(
        "--version", default=DEFAULT_VERSION,
        help=f"Package version (default: {DEFAULT_VERSION})"
    )
    parser.add_argument(
        "--template-only", action="store_true",
        help="Build only the template package"
    )
    parser.add_argument(
        "--site-only", action="store_true",
        help="Build only the full-install package"
    )
    args = parser.parse_args()

    print(f"Building packages (version {args.version})...")

    if not args.site_only:
        build_template(args.version)
    if not args.template_only:
        build_fullinstall(args.version)

    print("Done.")


if __name__ == "__main__":
    main()
