import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page-1)*QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  cors = CORS(app, resources={r'/api/*':{'origins':'*'}})
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow_-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, OPTIONS, DELETE')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.type).all()

    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
      })



  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    selection = Question.query.order_by(Question.id).all()
    total_questions = len(selection)
    current_questions = paginate_questions(request, selection)
    categories = Category.query.order_by(Category.type).all()


    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'categories': {category.id: category.type for category in categories},
      'current_category': None
      })   


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/question/<int:id>', methods=['DELETE'])
  def remove_question(id):
    try:
      question = Question.query.filter_by(id=id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success': True,
        'removed': id
        })

    except:
      abort(422)



  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def post_questions():
    body = request.get_json()
    new_question = body.get('question')
    new_answer = body.get('answer')
    new_difficulty = body.get('difficulty')
    new_category = body.get('category')


    if ((new_question is None) or (new_answer is None) 
        or (new_difficulty is None) or (new_category is None)):
      abort(422)

    

    try:
      question = Question(question=new_question,
                          answer=new_answer,
                          difficulty=new_difficulty,
                          category= new_category)
      question.insert()

      return jsonify({
        'success': True,
        'posted': question.id,
        'question_created': question.question,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
        })

    except:
      abort(422)


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/question/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm')

    if search_term:
      search_results = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

      if (len(selection)==0):
        abort(404)

      return jsonify({
                'success': True,
                'questions': [question.format() for question in search_results],
                'total_questions': len(search_results),
                'current_category': None
            })
    abort(404)


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions', methods=['GET'])
  def get_questions_by_category(id):
    try:
      questions = Question.query.filter_by(id=id).one_or_none()

      if (category is None):
        abort(400)

      selection = Question.query.filter_by(category=category.id).all()
      paginated = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'question': [question.format() for question in questions],
        'total_questions': len(questions),
        'current_category': category_id
        })


    except:
      abort(404)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quizz():
    body = request.get_json()
    previous_q = body.get('previous_questions')
    category_q = body.get('quiz_category')
    total = len(questions)


    if ((category_q is None) or (previous_q is None)):
      abort(400)
    if (category_q['id'] == 0):
      questions = Question.query.all()

    else:
      questions = Question.query.filter_by(category=category_q['id']).all()

    

    def random_questions():
      total = len(questions)
      return questions[random.randrange(0, total, 1)]

    def check_used(question):
      used = False
      for i in previous:
        if(i == question.id):
          used = True
      return used

    question = random_questions()

    while (check_used(question)):
      return jsonify({
        'success': True
        })

    return jsonify({
      'success':True,
      'question': question.format()
      })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success':False,
      'error': 404,
      'message': 'Questions base not found'
      }), 404



  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      'success':False,
      'error':422,
      'message':'Unprocessable entity'
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success':False,
      'error':400,
      'message':'Bad request'
      }), 400

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'success': False,
      'error':500,
      'message':'Internal server error occured'
      })
  
  return app

    