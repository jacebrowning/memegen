from .. import utils


def describe_gallery():
    def it_includes_language_and_meta_tags(expect):
        html = utils.html.gallery(
            [("/images/fry/a/b.png", "a / b")], columns=True, refresh=0
        )
        expect(html).contains('<html lang="en">')
        expect(html).contains('<meta charset="utf-8">')
        expect(html).contains(
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
        )

    def it_includes_alt_text(expect):
        html = utils.html.gallery(
            [("/images/fry/a/b.png", "Futurama Fry: a / b")], columns=True, refresh=0
        )
        expect(html).contains('alt="Futurama Fry: a / b"')

    def it_escapes_alt_text(expect):
        html = utils.html.gallery(
            [("/images/fry/a/b.png", """<b>"it's" & more</b>""")],
            columns=True,
            refresh=0,
        )
        expect(html).contains(
            'alt="&lt;b&gt;&quot;it&#x27;s&quot; &amp; more&lt;/b&gt;"'
        )
        expect(html).excludes("<b>")

    def describe_debug():
        def it_includes_alt_text_in_columns(expect):
            html = utils.html.gallery(
                [("/images/fry/a/b.png", "a / b")], columns=True, refresh=5
            )
            expect(html).contains('alt="a / b"')
            expect(html).contains("setInterval")

        def it_includes_alt_text_in_grid(expect):
            html = utils.html.gallery(
                [("/images/fry/a/b.png", "a / b")], columns=False, refresh=5
            )
            expect(html).contains('alt="a / b"')
            expect(html).contains('<html lang="en">')
