import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
import subway_resource.geoLine as line
import subway_resource.linkData as link
import subway_resource.nodeData as node
import os.path

# ----해결 과제----
# file load 속도가 너무 느림
# 똑같은 역 여러개 입력시 처리
# 검색기능
# 역 이름을 일부만 입력시 추천 역 이름? 밑에 표시
#   --역 이름 DB따로 필요?
# 지도 줌 기능
# 출발지 간의 평균 맞추기 : 지금은 각 출발지로부터 이동거리 총합의 최솟값
# 데이터 한번 읽어오면 계속 쓸수있게

INF = 99999999
File_path = "w2/output.txt"

# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("mainUI.ui")[0]

# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    dist = list()

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # QPixmap 객체 생성 후 이미지 파일을 이용하여 QPixmap에 사진 데이터 Load하고, Label을 이용하여 화면에 표시
        self.qPixmapFileVar = QPixmap()
        self.qPixmapFileVar.load("subway.png")
        self.qPixmapFileVar = self.qPixmapFileVar.scaledToWidth(1286)
        self.lbl_picture.setPixmap(self.qPixmapFileVar)

        self.people_group_1.hide()
        self.people_group_2.hide()
        self.people_group_3.hide()
        self.people_group_4.hide()

        # 명수 입력 부분
        self.people_number_lbl.returnPressed.connect(self.p_num_Function)

        # 출발지 입력 부분
        self.run_button.clicked.connect(self.get_start_pos)

    def p_num_Function(self):  # input box 숨기기
        self.p_num = int(self.people_number_lbl.text())
        self.people_group_1.hide()
        self.people_group_2.hide()
        self.people_group_3.hide()
        self.people_group_4.hide()
        self.make_input_place(self.p_num)

    def make_input_place(self, p_num):  # 이용 인원수에 따라 input box 보여주기
        if p_num == 1:
            self.people_group_1.show()
        elif p_num == 2:
            self.people_group_1.show()
            self.people_group_2.show()
        elif p_num == 3:
            self.people_group_1.show()
            self.people_group_2.show()
            self.people_group_3.show()
        elif p_num == 4:
            self.people_group_1.show()
            self.people_group_2.show()
            self.people_group_3.show()
            self.people_group_4.show()

    def get_start_pos(self):  # n명의 출발지점 가져온 후 길찾기 함수 호출
        p = list()

        if self.p_num > 0:
            p.append(self.p_start_lbl_1.text())
        if self.p_num > 1:
            p.append(self.p_start_lbl_2.text())
        if self.p_num > 2:
            p.append(self.p_start_lbl_3.text())
        if self.p_num > 3:
            p.append(self.p_start_lbl_4.text())

        destination_list = find_way(p, self.dist)

        result = ""
        for i in destination_list:
            result += i + "\n"

        self.result_consol.setText(result)


def find_way(p, dist):  # 길찾기 함수 시작
    print("in find way")

    length = len(node.nodeDataRaw)

    print(len(dist))

    if len(dist) == 0:
        dist = load_graph_file()

    min_dist = INF
    d_id = list()

    destination_id = -1

    p_id = get_id_from_name(p, length)

    if p_id[0] == -1:  # 잘못된 역 이름 Check
        d_id.append("")
        for i in range(len(p_id) - 1):
            d_id[0] += "\"" + p_id[i + 1] + "\"역은 잘못된 역 이름 입니다.\n"
        return d_id

    for i in range(length):  # 각 출발점으로부터 some station 까지의 거리의 총합이 가장 작은 station 구하기
        total_dist = 0  # 하나의 역만 구하지 말고 거리순으로 5개정도 구하기(해야할일)
        for j in p_id:  # count로 5개정도 차면 제일 먼저 들어온 애를 지워라
            total_dist += int(dist[j][i])
        if total_dist < min_dist:
            min_dist = total_dist
            del d_id[:]
            d_id.append(i)
        elif total_dist == min_dist:
            d_id.append(i)
        # print("i : %d  total_dist : %i  min_dist : %i  dest_id : %d" % (i, total_dist, min_dist, destination_id))

    return get_name_from_id(d_id, length)

def get_id_from_name(p, length):  # id list를 입력받아 name list로 바꿈
    print("in get_id")
    p_temp = p.copy()
    p_id = list()
    p_count = 0

    for i in range(length):
        for j in p_temp:
            if j == node.nodeDataRaw[i]['nm']:
                p_temp.pop(p_temp.index(j))
                p_id.append(i)
                p_count += 1
        if p_count == len(p):
            break

    if len(p_temp) != 0:
        print("잘못된 역 찾기 :", end="")
        print(p_temp)
        p_temp.insert(0, -1)
        return p_temp

    return p_id


def get_name_from_id(p_id, length):  # name list를 입력받아 id list로 바꿈
    print("in get name")

    p = list()
    p_count = 0
    p_id.sort()

    for i in range(length):
        if int(node.nodeDataRaw[i]['no']) == p_id[p_count]:
            p.append(node.nodeDataRaw[i]['nm'])
            p_count += 1
        if p_count == len(p_id):
            break
    return p


def load_graph_file():  # 그래프 파일 있으면 불러오고 없으면 생성
    print("in load graph")

    dist = list()
    length = len(node.nodeDataRaw)
    if os.path.isfile(File_path):  # 16초    불러오기
        print("file exist")
        with open(File_path, 'r') as output:
            for i in range(length):
                dist.append(list())
                line = output.readline()
                for j in range(length):
                    dist[i].append(line.split(' ')[j])
    else:
        print("file not exist")  # 2분31초  생성
        dist = make_graph(length)
    return dist


def make_graph_file(graph, length):  # 그래프 파일 만들기
    print("in make graph file")

    with open(File_path, 'w') as output:
        for i in range(length):
            for j in range(length):
                output.write('{0} '.format(str(graph[i][j])))
            output.write("\n")


def make_graph(length):  # 그래프 만들기 (nodeData와 linkData로)
    print("in make graph")

    link_length = len(link.linkDataRaw)

    graph = list()
    count = 0

    for i in range(length):
        graph.append(list())
        for j in range(length):
            if i == j:
                graph[i].append(0)
            else:
                graph[i].append(INF)

    for i in range(length):

        while count < len(link.linkDataRaw):
            if link.linkDataRaw[count][0] == i:
                if link.linkDataRaw[count][0] < length and link.linkDataRaw[count][1] < length:  # 없는 역과의 링크 체크
                    graph[i][link.linkDataRaw[count][1]] = link.linkDataRaw[count][2]
                    count += 1
                else:
                    count += 1
            else:
                break

    dist = floyd_warshall(graph, length)
    make_graph_file(dist, length)
    return dist


def floyd_warshall(a, n):
    print("in floyd_warshall")

    dist = a.copy()

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    # WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    myWindow.show()

    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
