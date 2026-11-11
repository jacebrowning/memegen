from .. import helpers


def describe_get_alt_text():
    def it_joins_lines_with_the_template_name(expect):
        alt = helpers.get_alt_text(["a", "b"], name="Futurama Fry")
        expect(alt) == "Futurama Fry: a / b"

    def it_skips_blank_lines(expect):
        alt = helpers.get_alt_text(["", "it's a trap!"], name="Ackbar")
        expect(alt) == "Ackbar: it's a trap!"

    def it_handles_missing_name(expect):
        alt = helpers.get_alt_text(["tests code", "in production"])
        expect(alt) == "tests code / in production"

    def it_handles_missing_lines(expect):
        alt = helpers.get_alt_text(["", ""], name="Blank")
        expect(alt) == "Blank"
