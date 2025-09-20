import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="자리 바꾸기 자동 생성기", layout="wide")
st.title("🪑 교실 자리 바꾸기 자동 생성기")

st.markdown("학생 명단을 입력하면 자동으로 무작위 자리 배치를 만들어 줍니다.")

# 학생 명단 입력
st.subheader("1. 학생 명단 입력")
students_text = st.text_area("학생 이름을 한 줄에 하나씩 입력하세요", height=200, placeholder="예: 홍길동\n김철수\n이영희")

# 교실 자리 설정
st.subheader("2. 자리 설정")
num_rows = st.number_input("교실의 줄(행) 수", min_value=1, max_value=10, value=5)
num_cols = st.number_input("교실의 칸(열) 수", min_value=1, max_value=10, value=6)

# 조건 설정
st.subheader("3. 조건 설정")
disable_front = st.checkbox("앞줄에 앉을 수 없는 학생 지정")
disable_pairs = st.checkbox("특정 학생끼리 짝이 되지 않도록 설정")

students = [s.strip() for s in students_text.split("\n") if s.strip()]

front_restricted = []
if disable_front and students:
    front_restricted = st.multiselect("앞줄에 앉지 못하는 학생 선택", students)

pair_restricted = []
if disable_pairs and students:
    pair_restricted = st.multiselect("같이 앉지 못하는 학생 2명 선택", students)

# 자리 배치 실행
if st.button("자리 배치 생성"):
    total_seats = num_rows * num_cols

    if len(students) > total_seats:
        st.error("⚠️ 학생 수가 자릿수보다 많습니다.")
    elif len(students) == 0:
        st.warning("학생 이름을 입력하세요.")
    else:
        # 자리 랜덤 섞기
        random.shuffle(students)

        # 앞줄 조건 적용
        if front_restricted:
            for student in front_restricted:
                if student in students:
                    idx = students.index(student)
                    if idx < num_cols:
                        students.append(students.pop(idx))

        # 짝 조건 적용 (간단 처리)
        if pair_restricted and len(pair_restricted) == 2:
            s1, s2 = pair_restricted
            if s1 in students and s2 in students:
                idx1, idx2 = students.index(s1), students.index(s2)
                if abs(idx1 - idx2) == 1:
                    students.append(students.pop(idx2))

        # 교실 배치표 생성
        seat_matrix = [["" for _ in range(num_cols)] for _ in range(num_rows)]
        idx = 0
        for r in range(num_rows):
            for c in range(num_cols):
                if idx < len(students):
                    seat_matrix[r][c] = students[idx]
                    idx += 1

        df = pd.DataFrame(seat_matrix)
        st.subheader("자리 배치 결과")
        st.dataframe(df)

        st.success("🎉 자리 배치가 완료되었습니다!")
        st.caption("앞줄은 DataFrame의 첫 번째 행으로 표시됩니다.")
