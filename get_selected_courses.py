import traceback
from get_grade import get_grade


def get_selected_courses(student_client):
    try:
        # 获取成绩信息
        grade = get_grade(student_client, output_type="grade")

        # 获取已选课程信息
        selected_courses_data = student_client.get_selected_courses().get("data", {})
        selected_courses = selected_courses_data.get("courses", [])

        # 按照学年学期降序排序
        # 对于没有学年学期参数的课程，则将学年学期设置为1970至1971学年第1学期，否则将无法排序
        selected_courses = sorted(
            selected_courses,
            key=lambda x: (
                (x["course_year"] if x["course_year"] else "1970-1971"),
                (x["course_semester"] if x["course_semester"] else "1"),
            ),
            reverse=True,
        )

        # 已选课程信息不为空时,处理未公布成绩的课程和异常课程
        if selected_courses:
            # 初始化空字典用于存储未公布成绩的课程,按学年学期分组
            ungraded_courses_by_semester = {}
            # 初始化空字典用于存储异常的课程,按学年学期分组
            abnormal_courses_by_semester = {}

            # 获取成绩列表中的class_id集合
            grade_class_ids = {course["class_id"] for course in grade} if grade else ""

            # 初始化输出内容
            selected_courses_filtering = ""

            # 遍历selected_courses和grade中的每个课程
            for course in selected_courses + (grade or []):
                # 获取课程的学年和学期
                try:
                    year, semester, seq = course["course_year"].split("-") + [
                        course["course_semester"]
                    ]
                except Exception:
                    pass

                # 构建年学期名称,例如 "a至b学年第c学期"
                yearsemester_name = f"{year}至{semester}学年第{seq}学期"

                # 判断课程是否未公布成绩或为异常课程
                if course["class_id"] not in grade_class_ids:
                    # 未公布成绩
                    ungraded_courses_by_semester.setdefault(
                        yearsemester_name, []
                    ).append(
                        f"{course['title'].replace('（', '(').replace('）', ')')} - {course['teacher']}"
                    )
                elif course["class_id"] not in {
                    course["class_id"] for course in selected_courses
                }:
                    # 异常课程
                    abnormal_courses_by_semester.setdefault(
                        yearsemester_name, []
                    ).append(
                        f"{course['title'].replace('（', '(').replace('）', ')')} - {course['teacher']}"
                    )

            # 构建输出内容
            if ungraded_courses_by_semester:
                # 存在未公布成绩的课程
                selected_courses_filtering += "------\n未公布成绩的课程："
                for i, (semester, courses) in enumerate(
                    ungraded_courses_by_semester.items()
                ):
                    if i > 0:
                        selected_courses_filtering += "\n------"
                    selected_courses_filtering += f"\n{semester}："
                    for course in courses:
                        selected_courses_filtering += f"\n{course}"

            if abnormal_courses_by_semester:
                # 存在异常的课程
                if ungraded_courses_by_semester:
                    # 如果存在课程,添加分隔线
                    selected_courses_filtering += "\n"
                selected_courses_filtering += "------\n异常的课程："
                for i, (semester, courses) in enumerate(
                    abnormal_courses_by_semester.items()
                ):
                    if i > 0:
                        selected_courses_filtering += "\n------"
                    selected_courses_filtering += f"\n{semester}："
                    for course in courses:
                        selected_courses_filtering += f"\n{course}"
        else:
            selected_courses_filtering = "------\n已选课程信息为空"
        return selected_courses_filtering

    except Exception:
        print(traceback.format_exc())
        return "------\n获取未公布成绩的课程或异常的课程时出错"
