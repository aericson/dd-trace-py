import json

from ddtrace.internal import _context


def test_django_simple_attack(client, test_spans, tracer):
    tracer._appsec_enabled = True
    # Hack: need to pass an argument to configure so that the processors are recreated
    tracer.configure(api_version="v0.4")
    assert client.get("/.git?q=1").status_code == 404
    root_span = test_spans.spans[0]
    assert "triggers" in json.loads(root_span.get_tag("_dd.appsec.json"))
    assert _context.get_item("http.request.uri", span=root_span) == "http://testserver/.git?q=1"
    assert _context.get_item("http.request.headers", span=root_span) is not None
    assert _context.get_item("http.request.query", span=root_span)["q"] == "1"


def test_django_querystrings(client, test_spans, tracer):
    tracer._appsec_enabled = True
    # Hack: need to pass an argument to configure so that the processors are recreated
    tracer.configure(api_version="v0.4")
    client.get("/?a=1&b&c=d")
    root_span = test_spans.spans[0]
    assert _context.get_item("http.request.query", span=root_span)["a"] == "1"
    assert _context.get_item("http.request.query", span=root_span)["b"] == ""
    assert _context.get_item("http.request.query", span=root_span)["c"] == "d"
    assert "d" not in _context.get_item("http.request.query", span=root_span)
    self.client.get("/")
    spans = self.pop_spans()
    root_span = spans[0]
    assert len(_context.get_item("http.request.query", span=root_span)) == 0
