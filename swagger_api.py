from flask import Flask, jsonify, request
from flasgger import Swagger
import sql_test
import random

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

@app.route('/api/<string:language>/', methods=['GET'])
def lan(language):

  """ 
  Get lan from the user. 
  --- 
  tags:
    - API lan 
  parameters: 
    - name: lan 
      in: path 
      type: string 
      required: true 
      description: the lan name 
    - name: size 
      in: query 
      type: integer 
      description: size of awesome 
  responses: 
    200: 
      description: lan 
      schema: 
        id: awesome 
        properties: 
          lan: 
            type: string 
            default: Lua 
            description: the lan 
          fea: 
            type: array 
            description: xx 
            items: 
              type: string 
              default: ['xx', 'yy', 'zz'] 
  """ 
  language = language.lower().strip() 
  fea = ['xx', 'yy', 'zz', 'tt', 'rr'] 
  size = int(request.args.get('size', 1))
  sizex = int(request.args.get('sizex', 1)) 
  return jsonify(language=language, fea=random.sample(fea, size),sizex=sizex)


@app.route('/get-value', methods=['GET'])
def get_value():
    # 方法 1
    return request.args['input_value']

    # 方法 2, 不帶預設值
    return request.args.get('input_value')
    
    # 方法 2, 帶預設值
    return request.args.get('input_value', 'No input')
    

if __name__ == '__main__':
    app.run(debug=True)
