# OCR-Doc-parser

## How it works
![image](https://user-images.githubusercontent.com/43296932/207932348-ef596f58-6781-4863-95cc-feac9ea0976b.png)


## Usage
```py
model = lp.models.Detectron2LayoutModel('lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
                                    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],)


langs = ['en']
for f in files:

    doc_parser_tool(
        f,
        output_dir,
        pdf_dir,
        langs = langs
    )
```
# Dockerfile
