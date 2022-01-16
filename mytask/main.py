import os
from unicodedata import category
from flask import Flask, render_template, request, redirect, session, url_for, jsonify,flash
from os.path import join, dirname, realpath

from flaskext.mysql import MySQL
from werkzeug.utils import secure_filename


import time

mysql = MySQL()
app = Flask(__name__)




# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/formm'
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = ""
app.config["MYSQL_DATABASE_DB"] = "task"
app.config["MYSQL_DATABASE_HOST"] = "localhost"

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/images/')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
mysql.init_app(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.secret_key = "123456"





#user authentication


@app.route('/signup', methods =["POST", "GET"])
def signUp():
    if request.method == "POST":
        name = request.form.get("name")            
        user_name = request.form.get("user_name")            
        password = request.form.get("password")            
               
        conn = mysql.connect()
        cur = conn.cursor()    
        cur.execute(''' insert into user_authentication (name,user_name,password) values(%s,%s,%s);''',[name,user_name,password])
        conn.commit()
        cur.close()            
        session["message"] = f"Conratulations dear {name} your account has been created"
        message = ""
        if session.get("message"):
            message = session.get("message")
        print(message)
        return redirect("/login")
    
   



@app.route('/login', methods=["GET","POST"])
def loginn():
    if session.get("user_name"):
        return redirect(url_for("home"))
    else:
        if request.method == "POST":
            user_name = request.form.get("user_name")
            password = request.form.get("password")
           
            conn = mysql.connect()
            cur = conn.cursor()
            cur.execute(" select * from user_authentication where user_name=%s;",[user_name])
            data = cur.fetchone()
            cur.close()
            conn.close()
            if data != None:
                if data[3] == password:
                    session["user_name"] = data[2]
                    
                    return redirect(url_for("home"))
                else:
                    session["error"] = "password doesn't match."
                    return redirect(url_for("loginn"))
            else:
                session["error"] = "user not exist."
                return redirect(url_for("loginn"))
        else:
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)

            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            return render_template("login.html", error=error,message=message)

@app.route("/logout",methods=["GET","POST"])
def logout():
    session.pop("user_name", None)
    return redirect(url_for("loginn"))


@app.route('/home', methods =["POST", "GET"])
def home():
    if session.get("user_name"):
        if request.method == "POST":
            return redirect(url_for("home"))
        else:
            return render_template("basic.html")
    else:
        return redirect(url_for("loginn"))




#add category section

@app.route('/category-add',methods=["POST","GET"])
def categoryAdd():
    if session.get("user_name"):
        if request.method == "POST":
            category_name = request.form.get("category_name")
            image = request.files.get("images")
            if image.filename != "":
                filename = image.filename
                filename = filename
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                conn = mysql.connect()
                cur = conn.cursor()
            conn = mysql.connect()
            cur = conn.cursor()
            cur.execute('''select category_name from category where category_name=%s;''',[category_name])
            data = cur.fetchone()
            if data is None:
                cur.execute(''' insert into category (category_name,category_image) values(%s,%s);''',[category_name,filename])
                conn.commit()
                cur.close()
                session["message"] = "New Category  Has Been added successfully."
            
                message = ""
                if session.get("message"):
                    message = session.get("message")
                session.pop("message", None)
                return render_template("category-add.html",message=message)
            
            else:
                session["error"] = f"{category_name} is already exist "
                error = ""
                if session.get("error"):
                    error = session.get("error")
                session.pop("error", None)
                
                return render_template("category-add.html",error=error)
        else:
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)
            return render_template("category-add.html",error=error,message=message)
    else:
        return redirect(url_for("loginn"))



@app.route('/category-list', methods =["POST", "GET"])
def categoryList():  
    if session.get("user_name"):     
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute(" select * from category ")
        category = cur.fetchall()

        conn.commit()
        cur.close()
        head = ["S.NO","CATEGORY NAME","Delete"] 
        error = ""
        if session.get("error"):
            error = session.get("error")
        session.pop("error", None)
        return render_template("category-list.html",category=category,head=head,error=error)



@app.route('/category-delete', methods =["POST", "GET"])
def categoryDelete():
    category_id = request.args.get("category_id")
    print(category_id,"cat id")
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(" delete from category where category_id =%s",[category_id])
    conn.commit()
    cur.close()
    conn.close()
    session["error"] = "Category Has Been Deleted"
 
    return redirect(url_for("categoryList")) 




# product
@app.route('/product-add',methods=["POST","GET"])
def productAdd():
    if session.get("user_name"):
        if request.method == "POST":
            category_id = request.form.get("category_id")
            title = request.form.get("title")
            date = request.form.get("date")
            des = request.form.get("des")
            price = request.form.get("price")
            image = request.files.get("images")
            if image.filename != "":
                filename = image.filename
                filename = filename
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                conn = mysql.connect()
                cur = conn.cursor()
            conn = mysql.connect()
            cur = conn.cursor()
            cur.execute('''select title from products where title=%s;''',[title])
            data = cur.fetchone()
            if data is None:
                cur.execute(''' insert into products (category_id,title,date,des,price,image) values(%s,%s,%s,%s,%s,%s);''',[category_id,title,date,des,price,filename])
                conn.commit()
                cur.close()
                session["message"] = "Product  Has Been added successfully."
            
                message = ""
                if session.get("message"):
                    message = session.get("message")
                session.pop("message", None)
                return render_template("category-add.html",message=message)
            
            else:
                session["error"] = f"{title} is already exist "
                error = ""
                if session.get("error"):
                    error = session.get("error")
                session.pop("error", None)
                
                return render_template("category-add.html",error=error)
        else:
            conn = mysql.connect()
            cur = conn.cursor()
            conn = mysql.connect()
            cur = conn.cursor()
            cur.execute(""" select * from category ;""")
            category = cur.fetchall()
            cur.execute(""" select * from products ;""")
            sub_category = cur.fetchall()
            conn.close()
            cur.close()
            message = ""
            if session.get("message"):
                message = session.get("message")
                session.pop("message", None)
            error = ""
            if session.get("error"):
                error = session.get("error")
                session.pop("error", None)
            return render_template("product-add.html",error=error,message=message,category=category,sub_category=sub_category)
    else:
        return redirect(url_for("loginn"))



@app.route('/products-list', methods =["POST", "GET"])
def productsList():  
    if session.get("user_name"):     
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute(" select * from products ")
        products = cur.fetchall()

        conn.commit()
        cur.close()
        head = ["S.NO","products NAME","Delete"] 
        error = ""
        if session.get("error"):
            error = session.get("error")
        session.pop("error", None)
        return render_template("products-list.html",products=products,head=head,error=error)



@app.route('/product-delete')
def productDelete():
    product_id = request.args.get("product_id")

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(" delete from products where product_id =%s",[product_id])
    conn.commit()
    cur.close()
    conn.close()
    session["error"] = "Category Has Been Deleted"
 
    return redirect(url_for("productsList")) 

















@app.route('/category')
def category():
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(''' select *  from category;''')
    data = cur.fetchall()
    print(data)
    cur.close()
    conn.close()
    return render_template('category.html', data=data)


@app.route('/sub-category')
def Subcategory():
    category_id = request.args.get("category_id")
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(''' select *  from products where category_id=%s;''',[category_id])
    data = cur.fetchall()
    print(data)
    cur.close()
    conn.close()
    return render_template('subcategory.html', data=data)








 





if __name__=="__main__":
    app.run(debug=True, port=2001)