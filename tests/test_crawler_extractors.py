from pipeline.crawler.extractors.nbe import extract_nbe
from pipeline.crawler.extractors.shadow import extract_shadow


def test_extract_nbe_uses_selectors_and_collects_pdf_links():
    html = """
    <html><head><title>NBE</title></head><body>
      <h1 class="entry-title">Directive on FXD</h1>
      <time class="entry-date" datetime="2026-05-01T12:30:00+00:00"></time>
      <div class="elementor-widget-text-editor">
        <p>Paragraph one.</p>
        <p>Paragraph two.</p>
      </div>
      <a href="/wp-content/uploads/2026/05/directive.pdf">PDF</a>
    </body></html>
    """
    out = extract_nbe(
        html=html,
        url="https://nbe.gov.et/files/fxd-04-2026/",
        link_metadata={"directive_type_code": "FXD", "directive_number": "04"},
    )

    assert out.title == "Directive on FXD"
    assert "Paragraph one." in out.content
    assert out.directive_type_code == "FXD"
    assert out.directive_number == "04"
    assert out.attachments and out.attachments[0]["type"] == "pdf"


def test_shadow_extractor_returns_best_effort_content():
    html = """
    <html>
      <head><title>Sample Headline - Site</title></head>
      <body>
        <div>tiny</div>
        <main>
          This is the biggest text block with enough characters to be selected.
          2026-05-01
        </main>
      </body>
    </html>
    """
    out = extract_shadow(html=html, url="https://example.com/news/1")
    assert out.title.startswith("Sample Headline")
    assert "biggest text block" in out.content
