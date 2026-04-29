import os
import requests

GEOSERVER_URL = "http://localhost:8080/geoserver"
USERNAME = "admin"
PASSWORD = "geoserver"

WORKSPACE = "agri_project"
STORE_NAME = "dss_store"
LAYER_NAME = "dss_class"
STYLE_NAME = "dss_final"

RASTER_PATH = r"D:\AGRI_PROJECT\dss_class.tif"

DSS_SLD = """<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0"
 xmlns="http://www.opengis.net/sld">

  <NamedLayer>
    <Name>dss_final</Name>
    <UserStyle>
      <Title>DSS 4 Class</Title>
      <FeatureTypeStyle>
        <Rule>
          <RasterSymbolizer>
            <ColorMap type="values">
              <ColorMapEntry color="#ffffff" quantity="0" opacity="0" label="Background"/>
              <ColorMapEntry color="#ffff00" quantity="1" label="Very Low"/>
              <ColorMapEntry color="#ff9900" quantity="2" label="Low"/>
              <ColorMapEntry color="#ff3366" quantity="3" label="Moderate"/>
              <ColorMapEntry color="#0000ff" quantity="4" label="High"/>
            </ColorMap>
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>

</StyledLayerDescriptor>
"""

def create_workspace():
    url = f"{GEOSERVER_URL}/rest/workspaces"
    headers = {"Content-Type": "text/xml"}
    data = f"<workspace><name>{WORKSPACE}</name></workspace>"

    r = requests.post(url, auth=(USERNAME, PASSWORD), headers=headers, data=data)

    if r.status_code in [200, 201]:
        print("✅ Workspace created")
    elif r.status_code == 500:
        print("⚠️ Workspace already exists")
    else:
        print("❌ Workspace error:", r.status_code, r.text)

def upload_raster():
    if not os.path.exists(RASTER_PATH):
        print("❌ Raster file not found:", RASTER_PATH)
        return

    url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/coveragestores/{STORE_NAME}/file.geotiff"

    with open(RASTER_PATH, "rb") as f:
        r = requests.put(
            url,
            auth=(USERNAME, PASSWORD),
            headers={"Content-Type": "image/tiff"},
            data=f
        )

    if r.status_code in [200, 201]:
        print("✅ DSS raster uploaded successfully")
    else:
        print("❌ Raster upload failed:", r.status_code, r.text)

def create_style():
    create_url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/styles"
    style_xml = f"""
    <style>
        <name>{STYLE_NAME}</name>
        <filename>{STYLE_NAME}.sld</filename>
    </style>
    """

    r = requests.post(
        create_url,
        auth=(USERNAME, PASSWORD),
        headers={"Content-Type": "text/xml"},
        data=style_xml
    )

    if r.status_code in [200, 201]:
        print("✅ Style created")
    elif r.status_code == 500:
        print("⚠️ Style already exists")
    else:
        print("❌ Style creation failed:", r.status_code, r.text)

def upload_sld():
    url = f"{GEOSERVER_URL}/rest/workspaces/{WORKSPACE}/styles/{STYLE_NAME}.sld"

    r = requests.put(
        url,
        auth=(USERNAME, PASSWORD),
        headers={"Content-Type": "application/vnd.ogc.sld+xml"},
        data=DSS_SLD
    )

    if r.status_code in [200, 201]:
        print("✅ SLD uploaded")
    else:
        print("❌ SLD upload failed:", r.status_code, r.text)

def apply_style():
    url = f"{GEOSERVER_URL}/rest/layers/{WORKSPACE}:{LAYER_NAME}"

    data = f"""
    <layer>
        <defaultStyle>
            <name>{STYLE_NAME}</name>
            <workspace>{WORKSPACE}</workspace>
        </defaultStyle>
    </layer>
    """

    r = requests.put(
        url,
        auth=(USERNAME, PASSWORD),
        headers={"Content-Type": "text/xml"},
        data=data
    )

    if r.status_code in [200, 201]:
        print("✅ Style applied to DSS layer")
    else:
        print("❌ Style apply failed:", r.status_code, r.text)

def check_layer():
    url = f"{GEOSERVER_URL}/rest/layers/{WORKSPACE}:{LAYER_NAME}.json"
    r = requests.get(url, auth=(USERNAME, PASSWORD))

    if r.status_code == 200:
        print("✅ Layer available in GeoServer")
        print("Preview URL:")
        print(
            f"{GEOSERVER_URL}/{WORKSPACE}/wms?"
            f"service=WMS&version=1.1.0&request=GetMap"
            f"&layers={WORKSPACE}:{LAYER_NAME}"
            f"&styles={STYLE_NAME}"
            f"&bbox=78.7,10.1,79.6,11.2"
            f"&width=768&height=768"
            f"&srs=EPSG:4326"
            f"&format=image/png"
            f"&transparent=true"
        )
    else:
        print("❌ Layer not found:", r.status_code, r.text)

if __name__ == "__main__":
    create_workspace()
    upload_raster()
    create_style()
    upload_sld()
    apply_style()
    check_layer()