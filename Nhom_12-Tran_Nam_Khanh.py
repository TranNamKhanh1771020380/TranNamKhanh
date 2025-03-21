import os
import pygad
import numpy as np
import pandas as pd
from datetime import datetime

time_slots = ["Sáng thứ 2", "Chiều thứ 2", "Tối thứ 2",
              "Sáng thứ 3", "Chiều thứ 3", "Tối thứ 3",
              "Sáng thứ 4", "Chiều thứ 4", "Tối thứ 4",
              "Sáng thứ 5", "Chiều thứ 5", "Tối thứ 5",
              "Sáng thứ 6", "Chiều thứ 6", "Sáng thứ 7", "Chiều thứ 7"]

subjects = {
    "Toán": "Bảng trắng",
    "Lý": "Phòng thí nghiệm",
    "Hóa": "Phòng thí nghiệm",
    "Sinh": "Phòng thí nghiệm",
    "Văn": "Bảng trắng",
    "Sử": "Bảng trắng",
    "Địa": "Bảng trắng",
    "Anh": "Máy chiếu",
    "Tin học": "Máy tính"
}

teachers = ["GV1", "GV2", "GV3", "GV4", "GV5", "GV6", "GV7", "GV8", "GV9", "GV10", "GV11"]

rooms = {
    "P201": {"sức chứa": 30, "thiết bị": "Bảng trắng"},
    "P202": {"sức chứa": 50, "thiết bị": "Máy chiếu"},
    "P203": {"sức chứa": 40, "thiết bị": "Bảng trắng"},
    "P204": {"sức chứa": 30, "thiết bị": "Phòng thí nghiệm"},
    "P205": {"sức chứa": 60, "thiết bị": "Máy chiếu"},
    "P206": {"sức chứa": 35, "thiết bị": "Bảng trắng"},
    "P207": {"sức chứa": 45, "thiết bị": "Máy tính"}
}

students_groups = {
    "Nhóm 1": 25,
    "Nhóm 2": 30,
    "Nhóm 3": 40,
    "Nhóm 4": 50,
    "Nhóm 5": 35,
    "Nhóm 6": 45
}

subject_to_index = {subject: i for i, subject in enumerate(subjects.keys())}
index_to_subject = {i: subject for subject, i in subject_to_index.items()}
room_to_index = {room: i for i, room in enumerate(rooms.keys())}
index_to_room = {i: room for room, i in room_to_index.items()}

num_classes = 60
num_genes = num_classes * 4

gene_space = []
for _ in range(num_classes):
    gene_space.extend([
        list(range(len(time_slots))),
        list(subject_to_index.values()),
        list(range(len(teachers))),
        list(room_to_index.values())
    ])

def fitness_function(ga_instance, solution, solution_idx):
    score = 0
    schedule = np.reshape(solution, (num_classes, 4))
    used_slots = {}

    for i, (t_idx, s_idx, g_idx, r_idx) in enumerate(schedule):
        time = time_slots[int(t_idx)]
        subject = index_to_subject[int(s_idx)]
        teacher = teachers[int(g_idx)]
        room = index_to_room[int(r_idx)]
        group = list(students_groups.keys())[i % len(students_groups)]

        if (teacher, time) in used_slots or (group, time) in used_slots or (room, time) in used_slots:
            score -= 100
        else:
            score += 10
            used_slots[(teacher, time)] = True
            used_slots[(group, time)] = True
            used_slots[(room, time)] = True

        if students_groups[group] > rooms[room]["sức chứa"]:
            score -= 50

        if subjects[subject] != rooms[room]["thiết bị"]:
            score -= 30

        if time.startswith("Sáng") and teacher in ["GV1", "GV2", "GV3", "GV9"]:
            score += 5
        if time.startswith("Chiều") and teacher in ["GV6", "GV7", "GV8", "GV10"]:
            score += 5
        if time.startswith("Tối") and teacher in ["GV11"]:
            score += 5

    return score

ga_instance = pygad.GA(
    num_generations=300,
    num_parents_mating=15,
    fitness_func=fitness_function,
    sol_per_pop=30,
    num_genes=num_genes,
    gene_space=gene_space
)

ga_instance.run()
best_solution = ga_instance.best_solution()[0]
best_schedule = np.reshape(best_solution, (num_classes, 4))

final_schedule = []
for i, (t_idx, s_idx, g_idx, r_idx) in enumerate(best_schedule):
    final_schedule.append([
        time_slots[int(t_idx)],
        index_to_subject[int(s_idx)],
        teachers[int(g_idx)],
        index_to_room[int(r_idx)],
        list(students_groups.keys())[i % len(students_groups)]
    ])

df = pd.DataFrame(final_schedule, columns=["Thời gian", "Môn học", "Giáo viên", "Phòng", "Nhóm SV"]).head(5)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
file_name = f"thoi_khoa_bieu_{timestamp}.xlsx"
df.to_excel(file_name, index=False)

print(f"Đã lưu 5 dòng thời khóa biểu vào file: {file_name}")
df.head()
