import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from peewee import *
import datetime
import time
from playhouse.shortcuts import model_to_dict

load_dotenv()
app = Flask(__name__)

# Database connection
if os.getenv("TESTING") == "true":
    db = SqliteDatabase(':memory:')
else:
    db = MySQLDatabase(
        os.getenv("MYSQL_DATABASE", "myportfoliodb"),
        user=os.getenv("MYSQL_USER", "myportfolio"),
        password=os.getenv("MYSQL_PASSWORD", "mypassword"),
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=3306
    )

# TimelinePost model definition
class TimelinePost(Model):
    id = AutoField()
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

# Connect and create table if not exists
try:
    db.connect()
    db.create_tables([TimelinePost], safe=True)
    print(f"Database connection successful: {db}")
except Exception as e:
    print(f"Database connection failed: {e}")

# Rate limiting storage
rate_limit_storage = {}

# Ensure db connection per request
@app.before_request
def _db_connect():
    if db.is_closed():
        db.connect()

@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()

base_url = "/"

navigation_items = [
    {'name': 'Home', 'url': base_url + '#profile', 'active': False},
    {'name': 'Experience', 'url': base_url + '#work-experience', 'active': False},
    {'name': 'Education', 'url': base_url + '#education', 'active': False},
    {'name': 'Hobbies', 'url': '/hobbies', 'active': False},
    {'name': 'Timeline', 'url': '/timeline', 'active': False},
    {'name': 'Visited Places', 'url': base_url + '#visited-places', 'active': False},
]

def get_navigation(current_page):
    nav_items = []
    for item in navigation_items:
        nav_item = item.copy()
        nav_item['active'] = (nav_item['url'] == current_page)
        nav_items.append(nav_item)
    return nav_items

# Data structures for dynamic content
work_experiences = [
    {
        'title': 'Senior Software Developer',
        'company': 'TechCorp Solutions',
        'duration': 'January 2020 - Present',
        'achievements': [
            'Led the development of cloud-native applications using AWS services, resulting in 40% improved scalability',
            'Implemented CI/CD pipelines using GitHub Actions and AWS CodePipeline',
            'Mentored junior developers and conducted code reviews to maintain high code quality'
        ]
    },
    {
        'title': 'Software Developer',
        'company': 'DataTech Systems',
        'duration': 'June 2017 - December 2019',
        'achievements': [
            'Developed and maintained data analytics platforms serving over 100,000 users',
            'Optimized database queries resulting in 60% faster response times',
            'Collaborated with cross-functional teams to deliver features on schedule'
        ]
    }
]

education = [
    {
        "degree": "Master of Science in Software Engineering",
        "school": "University of Technology",
        "duration": "August 2077 - May 2077",
        "achievements": [
            "Specialized in Cloud Computing and Distributed Systems",
            "Thesis: 'Optimizing Cloud-Based Data Processing for Large-Scale Applications'",
            "Participated in various hackathons and coding competitions"
        ]
    },
    {
        "degree": "Bachelor of Science in Computer Science",
        "school": "Tech University",
        "duration": "August 1337 - May 1337",
        "achievements": [
            "Graduated with Honors",
            "Relevant Coursework: Data Structures, Algorithms, Database Systems, Cloud Computing",
            "Capstone Project: Developed a cloud-based application for real-time data analytics"
        ]
    }
]

hobbies = [
    {
        'name': 'Photography',
        'description': 'Passionate about capturing moments and exploring different perspectives through the lens.',
        'details': 'I specialize in landscape and street photography. My favorite time to shoot is during golden hour, and I love experimenting with long exposure techniques.',
        'icon_color': '#1C539F'
    },
    {
        'name': 'Hiking',
        'description': 'Love exploring nature trails and challenging myself with different terrains.',
        'details': 'I regularly explore local trails and have completed several challenging mountain hikes. My goal is to hike at least one new trail every month.',
        'icon_color': '#d4851a'
    },
    {
        'name': 'Open Source',
        'description': 'Contributing to open source projects and building side projects.',
        'details': 'I actively contribute to various open source projects, mainly focusing on Python and JavaScript libraries. I believe in the power of community-driven development.',
        'icon_color': '#0c59ff'
    }
]

visited_locations = [
    {
        "name": "Paris, France",
        "coords": [48.8566, 2.3522],
        "description": "Visited the Eiffel Tower and Louvre Museum"
    },
    {
        "name": "Tokyo, Japan",
        "coords": [35.6762, 139.6503],
        "description": "Explored Shibuya and enjoyed authentic sushi"
    },
    {
        "name": "New York, USA",
        "coords": [40.7128, -74.0060],
        "description": "Saw Times Square and Central Park"
    },
    {
        "name": "Sydney, Australia",
        "coords": [-33.8688, 151.2093],
        "description": "Visited the Opera House and Bondi Beach"
    },
    {
        "name": "Bermuda Triangle",
        "coords": [25.0000, -71.0000],
        "description": "Met some aliens and they were friendly! They even gave me a ride in their spaceship."
    }
]

@app.route('/')
def index():
    return render_template('index.html',
                         title="MLH Fellow",
                         url=os.getenv("URL"),
                         name="Ace Perez",
                         role="Software Developer",
                         about_text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                         work_experiences=work_experiences,
                         education=education,
                         hobbies=hobbies,
                         navigation=get_navigation('/'),
                         visited_locations=visited_locations
                         )

@app.route('/hobbies')
def hobbies_page():
    return render_template('hobbies.html',
                         title="My Hobbies",
                         url=os.getenv("URL"),
                         hobbies=hobbies,
                         navigation=get_navigation('/hobbies'))

@app.route('/map')
def map_page():
    return render_template('map.html',
                         title="Places I've Visited",
                         url=os.getenv("URL"),
                         visited_locations=visited_locations,
                         navigation=get_navigation('/map'))

@app.route('/timeline')
def timeline_page():
    return render_template('timeline.html',
                         title="Timeline",
                         url=os.getenv("URL"),
                         navigation=get_navigation('/timeline'))

# POST endpoint to create a timeline post
@app.route('/api/timeline_post', methods=['POST'])
def post_timeline_post():
    # Rate limiting: 1 request per minute per IP
    global rate_limit_storage
    client_ip = request.remote_addr
    current_time = time.time()
    
    # Clean old entries (older than 1 minute)
    rate_limit_storage = {ip: timestamp for ip, timestamp in rate_limit_storage.items() 
                         if current_time - timestamp < 60}
    
    # Check if this IP has made a request in the last minute
    if client_ip in rate_limit_storage:
        return jsonify({
            'error': 'Rate limit exceeded. Please wait 1 minute before making another request.',
            'rate_limit': '1 request per minute'
        }), 429
    
    # Record this request
    rate_limit_storage[client_ip] = current_time
    
    name = request.form.get('name')
    email = request.form.get('email')
    content = request.form.get('content')
    
    # Validate input
    if not name or name.strip() == '':
        return jsonify({'error': 'Invalid name'}), 400
    
    if not content or content.strip() == '':
        return jsonify({'error': 'Invalid content'}), 400
    
    # Basic email validation
    if not email or '@' not in email or '.' not in email.split('@')[-1]:
        return jsonify({'error': 'Invalid email'}), 400
    
    timeline_post = TimelinePost.create(
        name=name,
        email=email,
        content=content
    )
    return model_to_dict(timeline_post), 201

# GET endpoint to retrieve all timeline posts
@app.route('/api/timeline_post', methods=['GET'])
def get_timeline_post():
    posts = TimelinePost.select().order_by(TimelinePost.created_at.desc())
    return jsonify([model_to_dict(post) for post in posts])

# DELETE endpoint to delete a timeline post by id
@app.route('/api/timeline_post/<int:post_id>', methods=['DELETE'])
def delete_timeline_post(post_id):
    try:
        post = TimelinePost.get(TimelinePost.id == post_id)
        post.delete_instance()
        return jsonify({'message': f'Timeline post {post_id} deleted successfully'}), 200
    except TimelinePost.DoesNotExist:
        return jsonify({'error': f'Timeline post with ID {post_id} not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to delete timeline post: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
