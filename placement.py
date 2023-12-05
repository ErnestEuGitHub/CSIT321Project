from flask import render_template, request, flash, session, redirect, url_for
from database import dbConnect
import bcrypt
from sqlalchemy import text


def generate_seeds(n):
    seeds = []
    current_seed = 1
    for i in range(n):
        seeds.append(current_seed)
        current_seed += 1
    return seeds

print(generate_seeds(15))