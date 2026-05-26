# Avatar

## Model requirements

Copied from: https://forum.shapespark.com/t/custom-video-meetings-avatars/4092/3

- Poly count: the lower the better, the best would be to not exceed 10.000 polygons but there is no
  hard limit.
- Model should be made from two body parts (objects named: head and torso) and display panel for
  video output (named: display, aspect ratio: 16:10)
- Head and torso can be made from single or multiple meshes, but meshes need to be grouped or named
  appropriately (example multi mesh naming: head_01, head_02, torso_01, torso_02)
- Head center should be placed in world origin (0, 0, 0), facing forward on Y axis.
- Model should use real world scale (1 unit == 1 meter)

## Model export

Avatar model is exported from Blender as .obj file with the following options:

- Forward: Y Forward
- Up: Z Up
- UV Coordinates: enabled
- Normals: enabled
- (Materials should be off)

## Configuration file

Avatar configuration file is a .json file, placed within the same directory as .obj file. It
contains the following fields:

- `model` - filename of the avatar model, ex: `avatar.obj`
- `displayLookAtCamera` - a boolean value telling if the display is automatically oriented to always
  look at the camera (optional, defaults to false)
- `rotateHeadInPortraitMode` - a boolean value telling if the head is to be rotated by 90 deg
  when the video stream is in portrait mode, irrelevant when `displayLookAtCamera` is true
  (optional, defaults to true)
- `meshes` - list of meshes that are part of the avatar, each element has to contain fields:
  - `group` - name of the avatar part, one of four: `head, torso, displayLandscape, displayPortrait`
  - `geometryName` - name of the geometry name in the model file.
  - `materialName` - name of the material specified in material list below. (optional, defaults to
    default material)
- `materials` - list of materials configurations, each element has to contain fields:
  - `name` - name of the material, ex: `white`
  - `baseColor` - base color of the material, ex: `[1.0, 1.0, 1.0]`
  - `baseColorTexture` - filename of the base color texture as `file` property,
    ex: `{"file": "white.png"}`. (optional)
  - `roughness` - roughness value of the material, ex: `0.5`
  - `metallic` - metallic value of the material, ex: `0.5`

## Example

See `example_custom_avatar.obj` + `example_custom_avatar.json` for example custom avatar model
and configuration.

## Textures

Textures are placed in the same directory as .obj file and must be referenced in the `materials`
section of .json configuration file. Each material has optional `baseColorTexture` property.

## Test custom avatar

Provide `WALK.AVATAR_JSON_URL_OVERRIDE` as url to local json file in `DevelConfig.js` file.

## Deploying custom avatar

Use the `upload-custom-user-asset.sh` tool from the shapespark repository to deploy a custom avatar:

    upload-custom-user-asset.sh <custom-avatar>.obj <storage-dir>
    upload-custom-user-asset.sh <custom-avatar>.json <storage-dir>

where `<storage-dir>` is the user storage directory in the scene assets bucket, as reported by
`backoffice.py users <username>`.

The assets are uploaded as:
`https://cdn0.shapespark.com/<storage-dir>/ASSETS/<custom-avatar>.{obj,json}`

Then, set the custom avatar JSON URL for the user in the cloudspark DB with:

```
BEGIN;
UPDATE "user" SET avatar_json_url = '<custom-avatar-json-url>' where username = '<username>';
COMMIT;
```

# Brotli encoding (not related to avatar)

File br.buf is a test file compressed by Brotli to check if
browser supports Brotli encoding.
