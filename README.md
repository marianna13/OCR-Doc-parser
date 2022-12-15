# OCR-Doc-parser

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
