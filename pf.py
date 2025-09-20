import streamlit as st
import pandas as pd

st.set_page_config(page_title="학급 투표/설문 앱", layout="wide")
st.title("📊 학급 투표 / 설문 앱")

# ---------------------------- 상태 저장 ----------------------------
if "polls" not in st.session_state:
    st.session_state.polls = []

if "mode" not in st.session_state:
    st.session_state.mode = "투표"

if "survey_mode" not in st.session_state:
    st.session_state.survey_mode = "자유 서술형"

if "allow_multiple" not in st.session_state:
    st.session_state.allow_multiple = True

# ---------------------------- 교사용 설정 ----------------------------
teacher_password = "teacher123"  # 원하는 비밀번호로 변경 가능
entered_password = st.sidebar.text_input("🔑 교사용 비밀번호 입력", type="password")

if entered_password == teacher_password:
    st.sidebar.markdown("### ⚙️ 설정 (교사용)")

    st.session_state.mode = st.sidebar.radio("모드 선택", ["투표", "설문조사"])

    if st.session_state.mode == "설문조사":
        st.session_state.survey_mode = st.sidebar.radio("설문 유형 선택", ["자유 서술형", "객관식(항목 선택)"])

    st.session_state.allow_multiple = st.sidebar.checkbox("중복 응답 허용", value=True)

    # 설문/투표 추가
    st.sidebar.markdown("---")
    st.sidebar.subheader("➕ 질문 추가")
    new_question = st.sidebar.text_input("질문 입력")
    new_options = st.sidebar.text_area("항목 입력 (줄바꿈으로 구분)", "예: 선택1\n선택2")

    if st.sidebar.button("질문 저장"):
        options = [o.strip() for o in new_options.split("\n") if o.strip()]
        st.session_state.polls.append({
            "question": new_question if new_question else "질문 없음",
            "options": options,
            "votes": {opt: 0 for opt in options},
            "responses": {}
        })

    # 초기화
    st.sidebar.markdown("---")
    if st.sidebar.button("초기화"):
        st.session_state.polls = []
        st.success("모든 질문과 데이터가 초기화되었습니다!")
else:
    st.sidebar.info("교사용 설정을 보려면 비밀번호를 입력하세요.")

# ---------------------------- 학생용 인터페이스 ----------------------------
st.subheader("1️⃣ 참여하기")
student_name = st.text_input("✏️ 이름을 입력하세요 (응답 제한 확인용)")

if not st.session_state.polls:
    st.info("먼저 교사용 사이드바에서 질문과 항목을 추가하세요.")
else:
    for idx, poll in enumerate(st.session_state.polls):
        st.markdown(f"**Q{idx+1}. {poll['question']}**")

        if st.session_state.mode == "투표":
            choice = st.radio("항목을 선택하세요:", poll["options"], key=f"vote_{idx}")
            if st.button("✅ 투표 제출", key=f"vote_btn_{idx}"):
                if not student_name:
                    st.warning("이름을 입력해야 투표할 수 있습니다.")
                elif (not st.session_state.allow_multiple) and (student_name in poll["responses"]):
                    st.error("이미 이 질문에 참여했습니다.")
                else:
                    poll["votes"][choice] += 1
                    poll["responses"][student_name] = choice
                    st.success(f"투표 완료! 선택한 항목: {choice}")

        elif st.session_state.mode == "설문조사":
            if st.session_state.survey_mode == "자유 서술형":
                answer = st.text_area("의견을 입력하세요:", key=f"survey_{idx}")
                if st.button("📝 설문 제출", key=f"survey_btn_{idx}"):
                    if not student_name:
                        st.warning("이름을 입력해야 설문할 수 있습니다.")
                    elif (not st.session_state.allow_multiple) and (student_name in poll["responses"]):
                        st.error("이미 이 질문에 참여했습니다.")
                    else:
                        poll["responses"][student_name] = answer
                        st.success("설문이 제출되었습니다!")
                        st.info(f"입력한 응답: {answer}")

            elif st.session_state.survey_mode == "객관식(항목 선택)":
                choice = st.radio("답변을 선택하세요:", poll["options"], key=f"survey_choice_{idx}")
                if st.button("📝 설문 제출", key=f"survey_btn_{idx}"):
                    if not student_name:
                        st.warning("이름을 입력해야 설문할 수 있습니다.")
                    elif (not st.session_state.allow_multiple) and (student_name in poll["responses"]):
                        st.error("이미 이 질문에 참여했습니다.")
                    else:
                        poll["votes"][choice] += 1
                        poll["responses"][student_name] = choice
                        st.success(f"설문 제출 완료! 선택한 답변: {choice}")

# ---------------------------- 결과 ----------------------------
st.subheader("2️⃣ 결과")
for idx, poll in enumerate(st.session_state.polls):
    st.markdown(f"### 📌 Q{idx+1}. {poll['question']}")

    if poll["votes"] and (st.session_state.mode == "투표" or (st.session_state.mode == "설문조사" and st.session_state.survey_mode == "객관식(항목 선택)")):
        df = pd.DataFrame({"항목": list(poll["votes"].keys()), "응답 수": list(poll["votes"].values())})
        col1, col2 = st.columns([2,1])
        with col1:
            st.bar_chart(df.set_index("항목"))
        with col2:
            st.table(df)

        if df["응답 수"].sum() > 0:
            winner = df.loc[df["응답 수"].idxmax(), "항목"]
            st.success(f"🏆 현재 1위: **{winner}**")
