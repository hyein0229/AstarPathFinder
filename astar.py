import pygame
import argparse
import random
import pygame_gui
import math
from radio_button import Radio

# argparse 를 이용한 인자 입력 받기
parser = argparse.ArgumentParser(description='a-star algorithm grid cell size')
parser.add_argument('-M', help="number of rows", type=int, default=30)  
parser.add_argument('-N', help="number of cols", type=int, default=30)
parser.add_argument('-o', help="obstacle_ratio", type=float, default=0.2)

args = parser.parse_args()
M = args.M # rows
N = args.N # cols
obstacle_num = M*N*args.o  # numbers of obstacles

# pygame setting
pygame.init()
screen = pygame.display.set_mode((770, 700))
screen.fill((255, 255, 255))
pygame.display.set_caption("A-star algorithm")

# grid_world 의 기본 화면 크기 지정
width, height = 600, 600
background = pygame.Surface((width,height))
background.fill((0, 0, 0))

# pygame gui setting
manager = pygame_gui.UIManager((770,700))
start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 625), (150, 50)),
                                                text="Start A* search",
                                                manager=manager)
random_wall_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((220, 625), (150, 50)),
                                                text="Random Walls",
                                                manager=manager)
reset_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((390, 625), (150, 50)),
                                                text="Reset",
                                                manager=manager)
# heuristic radio button
radio_group = []
mahattan_btn = Radio(screen, 610, 200, (230, 230, 230), 'manhattan', 1)
euclidean_btn = Radio(screen, 610, 230,  (230, 230, 230), 'euclidean', 2)
radio_group.append(mahattan_btn)
radio_group.append(euclidean_btn)
mahattan_btn.isChecked = True  # 기본은 manhattan 으로 설정
# heuristic label
font = pygame.font.SysFont('calibri', 25)
font_surf = font.render('heuristics', True, (0,0,0))
w, h = font.size('heuristics')
font_pos = (610, 160)

# Grid Cell Class
class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.f, self.g, self.h = 0, 0, 0
        self.wall = False
        self.parent = None

# 벽이면 빈 셀로, 빈 셀이면 벽으로 토글하는 함수
def toggle_wall(cell):
    global walls
    if cell != S and cell != G: # 시작점과 도착점이 아니면 토글
        if cell.wall == True:
            cell.wall = False
            walls.remove(cell)
        else:
            cell.wall = True
            walls.append(cell)

# 마우스의 x좌표, y좌표에 해당하는 grid cell 리턴
def get_cell_pos(pos):
    x = pos[0] // grid_w 
    y = pos[1] // grid_h 
    # grid_world 내부에 해당하는 지 범위 체크
    if 0 <= x < N and 0 <= y < M: 
        return grid[x][y]
    return None

# RESET 함수
def reset():
    global open_lst, closed_lst, path, walls
    open_lst = []
    closed_lst = []
    path = []
    # 모든 벽을 빈 셀로 만들기
    for c in walls:
        c.wall = False
    walls = []

# make random walls
def random_walls():
    global grid
    # 생성할 랜덤벽보다 남은 빈 셀이 적다면 랜덤벽을 형성하지 않도록 함
    if obstacle_num > M*N - (len(walls) + 2):
        return 
        
    cnt = obstacle_num
    while cnt > 0:
        # random grid cell position 
        x = random.randrange(0,N)
        y = random.randrange(0,M)

        # 빈 grid cell 인지 체크
        if not grid[x][y].wall and grid[x][y] != S and grid[x][y] != G:
            grid[x][y].wall = True
            walls.append(grid[x][y])
            cnt -= 1

def heuristic(n, dst, op):
    if op == 1:
        return abs(n.x - dst.x) + abs(n.y - dst.y)
    elif op == 2:
        return math.sqrt((n.x - dst.x)**2 + (n.y - dst.y)**2)

# 출발지-도착지 경로까지 노란 선 그리기
def draw_line(background, cell):
    if cell.parent == None:
        return

    px, py = cell.parent.x, cell.parent.y
    if py + 1 == cell.y and px == cell.x: # 부모로부터 위에서 오는 방향
        pygame.draw.line(background, (255, 255, 0), (cell.x*grid_w + grid_w//2, cell.y*grid_h - grid_h//2), (cell.x*grid_w + grid_w//2, cell.y*grid_h + grid_h//2),2)
    elif py - 1 == cell.y and px == cell.x: # 아래서 오는 방향
        pygame.draw.line(background, (255, 255, 0), (cell.x*grid_w + grid_w//2, cell.y*grid_h + + grid_h + grid_h//2), (cell.x*grid_w + grid_w//2, cell.y*grid_h + grid_h//2),2)
    elif py == cell.y and px + 1 == cell.x: # 왼쪽에서 오는 방향
        pygame.draw.line(background, (255, 255, 0), (cell.x*grid_w - grid_w//2, cell.y*grid_h + grid_h//2), (cell.x*grid_w + grid_w//2, cell.y*grid_h + grid_h//2),2)
    else: # 오른쪽에서 오는 방향
        pygame.draw.line(background, (255, 255, 0), (cell.x*grid_w + grid_w + grid_w//2, cell.y*grid_h + grid_h//2), (cell.x*grid_w + grid_w//2, cell.y*grid_h + grid_h//2),2)


# grid_world setting
grid_w = width // N   # grid cell width
grid_h = height // M   # grid cell height
# grid_world 세팅
grid = []
for x in range(N):
    col = []
    for y in range(M):
        col.append(Cell(x, y))
    grid.append(col)

open_lst = []   # 열린 목록
closed_lst = []  # 닫힌 목록
path = []  # S~G 까지의 찾은 최단 경로
walls = []  # 벽인 cell 기록
# 처음 S, G 위치 임의 지정
S = grid[N - N//2][M//2 - M//15]
G = grid[N - N//2][M - M//4]

def A_star():

    #상하좌우
    dx = [0, 0, -1, 1]
    dy = [-1, 1, 0, 0]

    global open_lst, closed_lst, path, walls, S, G
    isContinued = True # A star 종료 여부
    start_search = False  # START 버튼을 누르면 True
    found = False # 경로 찾음 여부
    is_make_wall = False # 벽을 만들 때(True), 삭제할 때(False)
    move_S = False # S를 드래그로 옮길 때 True
    move_G = False # G를 드래그로 옮길 때 True
    option = 1 # heuristic option, manhattan 일 때 1, euclidean 일 때 2

    clock = pygame.time.Clock()

    while isContinued:

        time_delta = clock.tick(60)/1000.0

        for event in pygame.event.get():
            # START 가 활성화되어 경로를 찾는 중에는 마우스 이벤트를 처리를 막음
            if start_search:
                continue
            
            # 버튼을 클릭했을 시 처리
            manager.process_events(event) 
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button:
                    print("START A* SEARCH")
                    start_search = True
                    found = False
                    open_lst = []
                    closed_lst = []
                    path = []
                    open_lst.append(S) # 출발점을 열린목록에 넣고 탐색 시작

                elif event.ui_element == random_wall_button:
                    print("Random Walls")
                    random_walls()

                elif event.ui_element == reset_button:
                    print("RESET")
                    found = False
                    start_search = False
                    reset() 

            # grid_world 에서의 마우스 이벤트 처리
            if event.type == pygame.QUIT: # 종료했을 시
                isContinued = False

            if event.type == pygame.MOUSEBUTTONDOWN: 
                pressed = pygame.mouse.get_pressed()
                pos = pygame.mouse.get_pos() 
                if pressed[0]:
                    if pos[0] > 600 or pos[1] > 600:
                        # radio button 처리
                        for btn in radio_group:
                            btn.update(pos)
                            if btn.isChecked is True:
                                if btn.id == 1: # manhattan 버튼을 눌렀을 때
                                    option = 1
                                else: # euclidean 버튼을 눌렀을 때
                                    option = 2
                            
                                # 누른 버튼이 아니면 나머지는 다 토글
                                for b in radio_group:
                                    if b != btn:
                                        b.isChecked = False
                        continue
                    cur = get_cell_pos(pos) 
                    if cur == None: # grid cell이 아닌 경우
                        continue
                    # 시작점이나 도착점을 클릭했을 시 이동시키기
                    if cur == S: 
                        move_S = True
                    elif cur == G:
                        move_G = True
                    # 빈 셀 클릭 시 벽 만들기 활성화
                    elif not cur.wall: 
                        is_make_wall = True
                        toggle_wall(cur)
                    else: # 벽 클릭 시 벽 제거
                        is_make_wall = False
                        toggle_wall(cur)

            elif event.type == pygame.MOUSEBUTTONUP: # 마우스를 뗐을 때
                # S, G 드래그 비활성화
                if move_S:
                    move_S = False
                if move_G:
                    move_G = False               

            elif event.type == pygame.MOUSEMOTION:
                pressed = pygame.mouse.get_pressed()
                pos = pygame.mouse.get_pos()
                if pressed[0]:
                    cur = get_cell_pos(pos)
                    if cur == None:
                        continue

                    # S 또는 G를 드래그로 옮길 시 빈 셀이면 현 마우스 위치의 cell를 S, G로 변경
                    if move_S and not cur.wall:
                        S = cur  
                    if move_G and not cur.wall:
                        G = cur
                    
                    if is_make_wall: # 벽 만들기가 활성화된 상태면
                        if not cur.wall: # 벽이 아닐때만 토글
                            toggle_wall(cur)
                    elif cur.wall: # 벽 삭제 중이면 벽일 때 토글
                        toggle_wall(cur)

        # 종료
        if not isContinued:
            break

        # Start A* search
        if not found and start_search:
            if len(open_lst) == 0:
                print("최단 경로를 찾지 못했습니다.")
                start_search = False 
                if len(closed_lst) > 1:
                    # explored nodes 중 가장 f 가 작은 노드 찾기
                    min_i = 1
                    for i in range(1, len(closed_lst)):
                        if closed_lst[i].f < closed_lst[min_i].f:
                            min_i = i

                    cur = closed_lst[min_i]
                    while cur:
                        path.append(cur)
                        cur = cur.parent

            else:
                # 열린목록에서 가장 작은 f 를 갖는 셀 찾기
                min_f = 0
                for i in range(len(open_lst)):
                    if open_lst[min_f].f > open_lst[i].f:
                        min_f = i

                selected = open_lst[min_f]

                # 선택된 셀은 열린 목록에서 제거하고 닫힌 목록으로 넣기
                open_lst.remove(selected)
                closed_lst.append(selected)

                # 도착점일 때
                if selected == G:
                    cur = selected
                    while cur:
                        path.append(cur)
                        cur = cur.parent

                    found = True
                    start_search = False
                    print("최단 경로를 찾았습니다!!")
                    print("최단경로길이:", len(path) - 1)
                    print("Explored nodes 개수:", len(closed_lst))

                # 아직 도착점이 아닐 때
                else:
                    # 상하좌우 인접한 셀 탐색
                    for i in range(4):
                        nx, ny = selected.x + dx[i], selected.y + dy[i]
                        if nx < 0 or nx >= N or ny < 0 or ny >= M: # 범위 체크
                            continue

                        neighbor = grid[nx][ny]

                        # 1. 인접한 셀이 벽이거나 이미 닫힌 목록에 있는 경우 무시한다.
                        if neighbor.wall or neighbor in closed_lst:
                            continue
                        
                        # 2. 열린 목록에 없다면 추가
                        if neighbor not in open_lst:
                            neighbor.g = selected.g + 1
                            neighbor.h = heuristic(neighbor, G, option)
                            neighbor.f = neighbor.g + neighbor.h
                            neighbor.parent = selected
                            open_lst.append(neighbor)

                        # 3. 열린 목록에 있다면 g값을 비교    
                        else:
                            if neighbor.g > selected.g + 1: # 더 낮은 경우 갱신
                                neighbor.g = selected.g + 1
                                neighbor.parent = selected
                                neighbor.f = neighbor.g + neighbor.h

        # grid_world 그리기
        background.fill((0, 0, 0))
        for x in range(N):
            for y in range(M):
                cell = grid[x][y]
                if cell.wall:
                    pygame.draw.rect(background, (128, 128, 128), (x*grid_w, y*grid_h, grid_w-1, grid_h-1))
                elif cell == S: # 출발점
                    pygame.draw.rect(background, (0, 100, 0), (x*grid_w, y*grid_h, grid_w-1, grid_h-1))
                elif cell == G: # 도착점
                    pygame.draw.rect(background, (255,0, 0), (x*grid_w, y*grid_h, grid_w-1, grid_h-1))
                elif cell in closed_lst: # 닫힌 목록에 있으면
                    pygame.draw.rect(background, (0, 204, 255), (x*grid_w, y*grid_h, grid_w-1, grid_h-1))
                elif cell in open_lst: # 열린 목록에 있으면
                    pygame.draw.rect(background, (190, 255, 0), (x*grid_w, y*grid_h, grid_w-1, grid_h-1))
                else: # 빈 셀
                    pygame.draw.rect(background, (255, 255, 255), (x*grid_w, y*grid_h, grid_w-1, grid_h-1))
        
        # 찾은 경로가 있다면 선 그리기
        if path:
            for cell in reversed(path):
                draw_line(background, cell)

        # pygame button
        screen.blit(font_surf, font_pos)
        pygame.draw.rect(screen, (0,0,0), (605, 187, 150, 70), 1)
        for btn in radio_group:
            btn.make_button()

        manager.update(time_delta)
        screen.blit(background, (0, 0))
        manager.draw_ui(screen)
        pygame.display.flip()

if __name__ == '__main__':
    A_star()
    pygame.quit()