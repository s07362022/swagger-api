from flask import Flask, jsonify
from flasgger import Swagger
import sql_test

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/api/classes', methods=['GET'])
def get_classes():
    """
    Get classes from the database.
    ---
    responses:
      200:
        description: A list of classes
        schema:
          type: array
          items:
            type: object
            properties:
              class_id:
                type: integer
                example: 1
              class_name:
                type: string
                example: "Math"
    """
    classes = sql_test.get_classes()
    return jsonify(classes)

if __name__ == '__main__':
    app.run(debug=True)
