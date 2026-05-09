from flask import jsonify


def success_response(data=None, message="success", code=0, status=200):
    return jsonify(
        {
            "code": code,
            "message": message,
            "data": data if data is not None else {},
        }
    ), status


def error_response(message, code=4000, errors=None, status=400):
    payload = {
        "code": code,
        "message": message,
    }

    if errors is not None:
        payload["errors"] = errors

    return jsonify(payload), status
