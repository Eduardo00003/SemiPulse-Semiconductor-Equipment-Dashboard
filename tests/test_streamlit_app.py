from streamlit.testing.v1 import AppTest


def test_streamlit_app_renders_without_import_errors() -> None:
    app = AppTest.from_file("app/streamlit_app.py")
    app.run(timeout=10)

    assert not app.exception
