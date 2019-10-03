# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:44:32 2019

@author: JUNG
"""

from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask import current_app as app
import module1

# 추가할 모듈이 있다면 추가
 
main= Blueprint('main', __name__, url_prefix='/')
learnmore = Blueprint('learnmore', __name__, url_prefix='/main/')
blog_list = Blueprint('blog_list', __name__, url_prefix='/main/')
 
@main.route('/main', methods=['GET'])
def index():
    print('index')
    return render_template('/main/index.html')

@main.route('/learnmore', methods=['GET'])
def learnmore():
    print('learnmore')
    return render_template('/main/learnmore.html')

@main.route('/loading', methods=['POST'])
def loading():
    print('loading')
    keyword = request.form['keyword']
    return render_template('/main/loading.html', keyword=keyword)


@main.route('/blog_list', methods=['POST'])
def blog_list():
    print('blog_list')
    keyword = request.form['keyword']
    result_list = module1.module1(keyword)
    return render_template('/main/blog_list.html', keyword=keyword, result_list = result_list)
