from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models import Transaction, db
from datetime import datetime
import json

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html", user=current_user)

@views.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        date = request.form.get('date')
        amount = request.form.get('amount')
        category = request.form.get('category')  # `or ''` not needed
        description = request.form.get('description', '')
        type = request.form.get('type')


        if not date:  
            flash('Date is required.', category='error')
            return redirect(url_for('views.dashboard'))
        if not amount:
            flash('Amount is required.', category='error')
            return redirect(url_for('views.dashboard'))
        if not category: 
            flash('Category is required.', category='error')
            return redirect(url_for('views.dashboard'))


        description = request.form.get('description', '')
        type = request.form.get('type', '')

        try:
            amount = float(amount)
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            
            new_transaction = Transaction(
                date=date_obj, amount=amount, category=category,
                description=description, type=type, user_id=current_user.id
            )
            db.session.add(new_transaction)
            db.session.commit()
        except ValueError:
            flash('Invalid data entered. Check inputs.', category='error')

        return redirect(url_for('views.dashboard'))

    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    income = sum(t.amount for t in transactions if t.type == 'income')
    expense = sum(t.amount for t in transactions if t.type == 'expense')
    balance = income - expense

    return render_template('dashboard.html', transactions=transactions, income=income, expense=expense, balance=balance)





@views.route('/delete-transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if transaction and transaction.user_id == current_user.id:
        db.session.delete(transaction)
        db.session.commit()
    else:
        flash('Transaction not found or unauthorized.', category='error')
    return redirect(url_for('views.dashboard'))


@views.route('/visualize', methods=['GET', 'POST'])
@login_required
def chart():
    income_vs_expense = db.session.query(
        db.func.sum(Transaction.amount), Transaction.type
    ).filter_by(user_id=current_user.id).group_by(Transaction.type).all()
    income_expense = {'income': 0, 'expense': 0}
    for total_amount, transaction_type in income_vs_expense:
        if transaction_type in income_expense:
            income_expense[transaction_type] = total_amount

    income_expense_list = [income_expense['income'], income_expense['expense']]


    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date).all()
    cumulative_balance = 0
    over_time_balance, dates_labels = [], []

    for transaction in transactions:
        cumulative_balance += transaction.amount if transaction.type == 'income' else -transaction.amount
        over_time_balance.append(cumulative_balance)
        dates_labels.append(transaction.date.strftime("%Y-%m-%d"))

    income_by_category = dict(db.session.query(Transaction.category, db.func.sum(Transaction.amount)).filter_by(user_id=current_user.id, type='income').group_by(Transaction.category).all())
    expense_by_category = dict(db.session.query(Transaction.category, db.func.sum(Transaction.amount)).filter_by(user_id=current_user.id, type='expense').group_by(Transaction.category).all())

    categories = set(income_by_category.keys()).union(expense_by_category.keys())
    income_data = [income_by_category.get(cat, 0) for cat in categories]
    expense_data = [expense_by_category.get(cat, 0) for cat in categories]

    return render_template(
        "visualize.html",
        income_vs_expense=json.dumps(income_expense_list),
        over_time_balance=json.dumps(over_time_balance),
        dates_label=json.dumps(dates_labels),
        categories=json.dumps(list(categories)),
        income_data=json.dumps(income_data),
        expense_data=json.dumps(expense_data),
    )
