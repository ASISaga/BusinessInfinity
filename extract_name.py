def extract_name(req):
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = None
        if req_body:
            name = req_body.get('name')
    if name:
        return f"Hello, {name}. This HTTP triggered function executed successfully.", 200
    else:
        return (
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            200
        )
