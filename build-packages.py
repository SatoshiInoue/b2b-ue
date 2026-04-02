#!/usr/bin/env python3
"""
Build script — generates two AEM content packages from content-package/

  b2b-ue-template-{VERSION}.zip
      Template-only package. Installs the Quick Site Creation template at
      /conf/global/site-templates/b2b-ue-1.0.0/.  Developer then creates the
      site manually via Sites → Create → Site from Template.

  b2b-ue-site-{VERSION}.zip
      Full-install package. Installs both the template AND all site content
      directly (/content/b2b-ue, /content/dam/b2b-ue, /conf/b2b-ue).
      Uses merge mode for conf/content — safe to reinstall without wiping
      AEM-managed configuration. DAM and template use replace mode.

      CF model nodes (/conf/b2b-ue/settings/dam/cfm/models/) are excluded
      because they require dam:AssetModel which may not be available on all
      AEM Cloud instances. Add CF models manually via AEM Author if needed.

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
import os
import zipfile

CONTENT_PKG_DIR = "content-package"
SITE_ZIP_REL = "jcr_root/conf/global/site-templates/b2b-ue-1.0.0/site.zip"

# Paths inside site.zip to skip in the full-install package.
# dam:AssetModel node type may not exist on all AEM Cloud instances.
SITE_ZIP_SKIP_PREFIXES = (
    "META-INF",
    "jcr_root/conf/b2b-ue/settings/dam/cfm/models",
)

DEFAULT_VERSION = "1.0.0"


def _read_src(rel_path: str) -> bytes:
    full = os.path.join(CONTENT_PKG_DIR, rel_path)
    with open(full, "rb") as f:
        return f.read()


def build_template(version: str) -> str:
    """
    Template-only package — mirrors content-package/ 1:1.
    Install via Package Manager, then create site via Quick Site Creation.
    """
    out = f"b2b-ue-template-{version}.zip"
    if os.path.exists(out):
        os.remove(out)

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(CONTENT_PKG_DIR):
            for fname in files:
                full = os.path.join(root, fname)
                arc = os.path.relpath(full, CONTENT_PKG_DIR)
                z.write(full, arc)

    print(f"  [template]      {out}  ({os.path.getsize(out) // 1024} KB)")
    return out


def build_fullinstall(version: str) -> str:
    """
    Full-install package — template + all site content in one package.

    Filter modes:
      /conf/global/site-templates  → replace  (fixed, predictable structure)
      /conf/b2b-ue                 → merge    (preserve AEM-managed settings)
      /content/b2b-ue              → merge    (preserve site-level properties
                                               set by Quick Site Creation)
      /content/dam/b2b-ue          → replace  (fully controlled asset set)

    Using merge for conf/content means reinstall adds/updates nodes from the
    package but does NOT delete nodes that exist in AEM but not in the package.
    This is intentional — it keeps Quick Site Creation's configuration intact.
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
  <!-- Site configuration: merge — preserves AEM-managed settings.
       CF model nodes are excluded (see build-packages.py SITE_ZIP_SKIP_PREFIXES). -->
  <filter root="/conf/b2b-ue"/>
  <!-- Page content: merge — preserves site-level properties (cq:conf,
       sling:configRef etc.) that Quick Site Creation writes to the root page. -->
  <filter root="/content/b2b-ue"/>
  <!-- DAM assets: replace — fully controlled by this package -->
  <filter root="/content/dam/b2b-ue" mode="replace"/>
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

    skipped = []

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

        # jcr_root from site.zip (page content, DAM, conf/b2b-ue)
        # Skip META-INF (already written above) and excluded paths.
        with zipfile.ZipFile(site_zip_path, "r") as site_z:
            for item in site_z.infolist():
                if any(item.filename.startswith(p) for p in SITE_ZIP_SKIP_PREFIXES):
                    skipped.append(item.filename)
                    continue
                z.writestr(item.filename, site_z.read(item.filename))

    if skipped:
        print(f"  [full install]  skipped {len(skipped)} excluded entries "
              f"(CF models / META-INF)")
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
