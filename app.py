from flask import Flask, render_template, redirect, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
from datetime import timedelta

app = Flask(__name__)
oauth = OAuth(app)
app.secret_key = 'd40e6a1f4db7df587ca7d201422c5f6c' # 用'generate_self_secret.py'生成
app.permanent_session_lifetime = timedelta(hours=1)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['GITHUB_CLIENT_ID'] = "7f9a6cf785b3135922a0"
app.config['GITHUB_CLIENT_SECRET'] = "0eba3a2d8b33841456599fd670393619cb60d074"

github = oauth.register(
    name='github',
    client_id=app.config['GITHUB_CLIENT_ID'],
    client_secret=app.config['GITHUB_CLIENT_SECRET'],
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    api_base_url='https://api.github.com/',
    redirect_uri='http://127.0.0.1:5000/login/github/authorize',
    client_kwargs={'scope': 'user:email'},
)

@app.route('/')
def index():
    if 'github_username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)

@app.route('/login/github/authorize')
def github_authorize():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    resp = github.get('/user').json()
    print(f"\n{resp}\n")

    session['github_data'] = {
        'username': resp['login'],
        'id':resp['id'],
        'email': resp.get('email', 'No email provided by GitHub'),
        'avatar_url': resp['avatar_url'],
        'bio': resp.get('bio', 'No bio provided by GitHub'),
        'public_repos': resp['public_repos'],
        'followers': resp['followers'],
        'following': resp['following'],
        'created_at': resp['created_at'],
        'updated_at':resp['updated_at']
    }

    print("You are successfully signed in using github")
    return redirect(url_for('dashboard'))

# http://127.0.0.1:5000/dashboard
@app.route('/dashboard')
def dashboard():
    if 'github_data' not in session:
        print("User haven't login.")
        return redirect(url_for('index'))
    print("Store User Data:", session['github_data'])
    return render_template('dashboard.html', user=session['github_data'])

@app.route('/logout')
def logout():
    session.pop('github_data', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)


'''

app = Flask(__name__)

GITHUB_API_URL = "https://api.github.com"
USERNAME = "AlexWeeeng22"  # 替换为你的GitHub用户名
TOKEN = "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"  # 替换为你的API令牌，建议使用环境变量或其他方法来安全地存储这个令牌
                                                    # 不建议直接在代码里中这么做，推荐使用os.environ来储存
                                                    # 但我的这个账号里也没什么东西，就姑且写我自己的
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


# http://127.0.0.1:5000/private_repos
@app.route('/private_repos', methods=['GET'])
def get_private_repositories():
    try:
        response = requests.get(f"{GITHUB_API_URL}/user/repos", headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # 打印整齐的 JSON 数据到控制台
            print(json.dumps(data, indent=4))

            # 如果只想返回私有仓库，你可以使用列表解析来过滤数据
            # private_repos = [repo for repo in data if repo["private"]]
            # return jsonify(private_repos)

            return jsonify(data)
        else:
            return jsonify({"error": "Cannot fetch data", "github_message": response.text}), response.status_code
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/events', methods=['GET'])
def get_user_events():
    response = requests.get(f"{GITHUB_API_URL}/users/{USERNAME}/events", headers=headers)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Cannot fetch data"}), response.status_code
'''
