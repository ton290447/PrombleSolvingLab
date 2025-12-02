#เมื่อรันเสร็จจะมีไฟล์ calculator เกิดขึ้นมา
import streamlit as st

def get_number_input(label):
    return st.number_input(label, value=0.0, step=0.1, format="%.2f")

def get_operator_input(label):
    valid_operators = ['+', '-', '*', '/', '%']
    return st.selectbox(label, valid_operators)

def calculate(num1, num2, operator):
    if operator == '+':
        return num1 + num2
    elif operator == '-':
        return num1 - num2
    elif operator == '*':
        return num1 * num2
    elif operator == '/':
        if num2 == 0:
            st.error("ข้อผิดพลาด: ไม่สามารถหารด้วยศูนย์ได้!")
            return None
        return num1 / num2
    elif operator == '%':
        if num2 == 0:
            st.error("ข้อผิดพลาด: ไม่สามารถหารด้วยศูนย์ได้!")
            return None
        return num1 % num2
    return None # Should not be reached if operator is validated

st.title('My Calculator')

# Get inputs from the user
num1 = get_number_input("ป้อนตัวเลขแรก:")
num2 = get_number_input("ป้อนตัวเลขที่สอง:")
operator = get_operator_input("เลือกตัวดำเนินการ:")

# Perform calculation when the button is clicked
if st.button('คำนวณ'):
    result = calculate(num1, num2, operator)
    if result is not None:
        st.success(f"ผลลัพธ์: {num1} {operator} {num2} = {result}")
