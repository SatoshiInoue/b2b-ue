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
      Uses mode="replace" on all filters — safe to reinstall / overwrite.

Usage:
    python3 build-packages.py           # builds both, version from VERSION below
    python3 build-packages.py --version 1.2.0

Source of truth:
    content-package/                    # package source (edit this)
      jcr_root/conf/global/site-templates/b2b-ue-1.0.0/
        site.zip                        # inner package — rebuild with Python
                                        # scripts if page content changes
      META-INF/vault/
        config.xml                      # shared, copied into both packages
        filter.xml                      # used only for template package
        properties.xml                  # used only for template package
"""

import argparse
import os
import zipfile

CONTENT_PKG_DIR = "content-package"
SITE_ZIP_REL = "jcr_root/conf/global/site-templates/b2b-ue-1.0.0/site.zip"

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
        for root, _dirs, files in os.walk(CONTENT_PKG_DIR):
            for fname in files:
                full = os.path.join(root, fname)
                arc = os.path.relpath(full, CONTENT_PKG_DIR)
                z.write(full, arc)

    print(f"  [template]      {out}  ({os.path.getsize(out)//1024} KB)")
    return out


def build_fullinstall(version: str) -> str:
    """
    Full-install package — template + all site content in one package.
    Safe to reinstall: mode="replace" wipes and replaces each path.
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
  <!-- Site template — Quick Site Creation still works after this package -->
  <filter root="/conf/global/site-templates/b2b-ue-1.0.0" mode="replace"/>
  <!-- Site configuration (CF models, settings) -->
  <filter root="/conf/b2b-ue" mode="replace"/>
  <!-- Page content -->
  <filter root="/content/b2b-ue" mode="replace"/>
  <!-- DAM assets -->
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
  <entry key="description">B2B UE — Full site install (template + content). Reinstall-safe.</entry>
  <entry key="requiresRoot">false</entry>
  <entry key="packageType">content</entry>
</properties>
"""

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        # META-INF — custom filter + properties, shared config
        z.writestr("META-INF/vault/filter.xml", filter_xml)
        z.writestr("META-INF/vault/properties.xml", properties_xml)
        z.writestr("META-INF/vault/config.xml",
                   _read_src("META-INF/vault/config.xml").decode())

        # jcr_root from content-package (the site template tree)
        src_jcr = os.path.join(CONTENT_PKG_DIR, "jcr_root")
        for root, _dirs, files in os.walk(src_jcr):
            for fname in files:
                full = os.path.join(root, fname)
                arc = os.path.relpath(full, CONTENT_PKG_DIR)
                z.write(full, arc)

        # jcr_root from site.zip (page content, DAM, conf/b2b-ue)
        # Skip META-INF — we already wrote our own above
        with zipfile.ZipFile(site_zip_path, "r") as site_z:
            for item in site_z.infolist():
                if item.filename.startswith("META-INF"):
                    continue
                z.writestr(item.filename, site_z.read(item.filename))

    print(f"  [full install]  {out}  ({os.path.getsize(out)//1024} KB)")
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
