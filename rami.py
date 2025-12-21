from enum import Enum
import numpy as np
from numpy import random
import time 
from copy import deepcopy
from collections import deque
from queue import PriorityQueue




# ! cost USC
dirctions = np.array(['up' , 'right' , 'down' , 'left'])
dirctionForDFS = ''
costUSC = 0

opened = 0
#! score 
numOfCoin = 0
numOfBall = 0

class CellType(Enum) :
    WALL = "🧱"
    BASKET = "🗑️"
    EMPTY = "-"
    BALL = "🏀"
    COIN = "🪙"
    BOX = "📦"

class Cell :
    def __init__(self , x , y , type ) -> None:
        self.x = x 
        self.y = y 
        self.type = type
    
    def __str__(self) -> str:
        return self.type.value

class State :
    def __init__(self , rows , cols ,board) -> None:
        self.rows = rows
        self.cols = cols
        self.board = board
        self.parent = None 
        self.depth = 1 
        self.getCords()
    
    def __str__(self) -> str:
        result = "" 
        for row in self.board:
            for cell in row :
                result += f"{str(cell)}\t"
            result  += "\n"
        return result 
        # return result
    
    def getCords(self) :
        self.balls_cords = []
        self.basket_cords = []
        self.coins_cords = []
        self.box_cords = []
        for row in self.board:
            for cell in row:
                if cell.type == CellType.BALL:
                    self.balls_cords.append({'row' : cell.x  ,  'col' : cell.y})
                elif cell.type == CellType.BASKET:
                    self.basket_cords.append({'row' : cell.x  ,  'col' : cell.y})
                elif cell.type == CellType.BOX :
                    self.box_cords.append({'row' : cell.x  ,  'col' : cell.y})
                elif cell.type == CellType.COIN : 
                    self.coins_cords.append({'row' : cell.x  ,  'col' : cell.y})
        
        self.ballsrow =  np.array([i['row'] for i in self.balls_cords])
        self.ballscol =  np.array([i['col'] for i in self.balls_cords])
        
        self.basketrow = np.array([i['row'] for i in self.basket_cords])
        self.basketcol = np.array([i['col'] for i in self.basket_cords])
        
        self.coinrow = np.array([i['row'] for i in self.coins_cords])
        self.coincol = np.array([i['col'] for i in self.coins_cords])
        
        self.boxrow = np.array([i['row'] for i in self.box_cords])
        self.boxcol = np.array([i['col'] for i in self.box_cords])
        
        return self.balls_cords , self.basket_cords , self.coins_cords , self.box_cords
    
    def compireState(self , state, other):
        numberBallState1 = len(state.balls_cords)
        numberBoxState1 = len(state.box_cords)
        numberCoinState1 = len(state.coins_cords)
        numberBasketState1 = len(state.basket_cords)
        
        numberBallState2 = len(other.balls_cords)
        numberBoxState2 = len(other.box_cords)
        numberCoinState2 = len(other.coins_cords)
        numberBasketState2 = len(other.basket_cords)
        
        state1 = numberBallState1 + numberBoxState1 + numberBasketState1 + numberCoinState1
        state2 = numberBallState2 + numberBoxState2 + numberBasketState2 + numberCoinState2
        
        if state1 < state2 :
            # return state1 
            return True
        elif state2 < state1:
            # return state2
            return False
        else :
            return False
    
    def goal(self , dirct) :
        global numOfBall , numOfCoin 
        for coin in self.coins_cords:
            for basket in self.basket_cords :
                if coin['row'] + 1 == basket['row'] and coin['col'] == basket['col'] and  (dirct == 'down' or dirct == 'up')  :
                    self.coins_cords.remove(coin)
                    self.board[coin['row']][coin['col']].type = CellType.EMPTY
                    numOfCoin = numOfCoin + 1
        
        for ball in self.balls_cords:
            for basket in self.basket_cords :
                if ball['row'] + 1  == basket['row'] and ball['col'] == basket['col'] and  (dirct == 'down' or dirct == 'up')  :
                    self.balls_cords.remove(ball)
                    self.board[ball['row']][ball['col']].type = CellType.EMPTY
                    numOfBall = numOfBall + 1
    
    def isGoal(self , dirct1) :
        global dirctionForDFS
        if dirct1 == ' ' :
            dirct1 = dirctionForDFS
        self.goal(dirct1)
        if not self.balls_cords :
            return True
        else:
            return False
    
    def isVaildMove(self , x , y) :
        if x < 0  :
            return False
        
        elif y < 0 :
            return False
        
        elif x >= self.rows :
            return False 
        
        elif y >= self.cols:
            return False 
        
        elif self.board[x][y].type == CellType.EMPTY:
            return True 
        
        else :
            return False
    
    def getNextStates(self , game , algo):
        global dirctionForDFS
        global dirctions
        global costUSC
        global opened 
        nextStates = []
        statesUCS = []
        new_dirctions = random.permutation(dirctions) 
        opened += 1 
        for dirct in new_dirctions :
            dirctionForDFS = dirct
            newBoard = deepcopy(self)
            costUSC = 0
            for _ in range(self.cols):
                game.move(dirct) 
            self.goal(dirct)
            nextStates.append(newBoard)
            statesUCS.append(self.stateUCS(newBoard , costUSC))
            newBoard.parent = deepcopy(self)
        if algo == "UCS" :
            return statesUCS
        else:
            return nextStates
    
    def stateUCS(self , state , cost):
        stateUCS = []
        stateUCS.append((state , cost))
        return stateUCS


#! compare UCS
class StateWrapper:
    def __init__(self, state, cost):
        self.state = state
        self.cost = cost
    
    def __lt__(self, other):
        if self.cost == other.cost:
            return self.state.compireState(self.state , other.state)
        else:
            return self.cost < other.cost

#! compare A* 
class StateWrapper_A_star:
    def __init__(self, state, cost, heuristic):
        self.state = state
        self.cost = cost
        self.heuristic = heuristic
    
    def __lt__(self, other) :
        if (self.cost + self.heuristic) == (other.cost + other.heuristic) :
            return (self.cost + self.heuristic) == (other.cost + other.heuristic) and self.state.compireState(self.state , other.state)
        else :
            return (self.cost + self.heuristic) < (other.cost + other.heuristic) 

class Game :
    def __init__(self , init_state , x) -> None:
        self.init_state = init_state
        self.current_state = deepcopy(init_state)
        
        
        self.states = []
        self.states.append(init_state)
        
        self.stack = []
        self.stack.append(init_state)
        self.visited = []
        self.visited.append(init_state)
        
        #! user play
        if x == 1 :
            self.user()
        
        #! DFS
        elif x == 2 :
            start_time = time.time()
            self.dfs()
            end_time = time.time()
            excutation_time = end_time - start_time
            print(f"excutation_time {excutation_time}")
        
        #! BFS
        elif x == 3 :
            start_time = time.time()
            self.bfs()
            end_time = time.time()
            excutation_time = end_time - start_time
            print(f"excutation_time {excutation_time}")
        
        #! UCS
        elif x == 4 :
            start_time = time.time()
            self.ucs()
            end_time = time.time()
            excutation_time = end_time - start_time
            print(f"excutation_time {excutation_time}")
        
        #! A*
        elif x == 5 :
            start_time = time.time()
            self.a_star()
            end_time = time.time()
            excutation_time = end_time - start_time
            print(f"excutation_time {excutation_time}")
        
        elif x == 6 :
            start_time = time.time()
            self.hill_climbing()
            end_time = time.time()
            excutation_time = end_time - start_time
            print(f"excutation_time {excutation_time}")
        else :
            print("please enter right number 1 , 2 , 3 , 4 or 5")
        
        if x != 1 :
            i = 0
            self.solution = []
            self.solution.append(self.current_state)
            while self.current_state.parent is not None :
                self.solution.append(self.current_state.parent)
                self.current_state = self.current_state.parent
                
            for state in reversed(self.solution) :
                i += 1
                print(f"{i} : \n")
                print(state)
    
    def user(self) :
        global costUSC
        dirct = ''
        while not self.current_state.isGoal(dirct) :
            print(self.current_state)
            print("_______________________________")
            print(" W : up\n S : down\n D : right\n A : left")
            user_input = input()
            if user_input == "w" :
                dirct = "up"
                costUSC = 0
                for _ in range(self.current_state.board.shape[1] ):
                    self.move("up")
                self.states.append(deepcopy(self.current_state))
            elif user_input == "s" :
                dirct = "down"
                for _ in range(self.current_state.board.shape[1] ):
                    self.move("down")
                self.states.append(deepcopy(self.current_state))
            elif user_input == "d" : 
                dirct = "right"
                for _ in range(self.current_state.board.shape[1]  ):
                    self.move("right")
                self.states.append(deepcopy(self.current_state))
            elif user_input == "a" :  
                dirct = "left"
                for _ in range(self.current_state.board.shape[1] ):
                    self.move("left")
                self.states.append(deepcopy(self.current_state))
            else : print("please type w, s , d or a for move")
        print("WIIIIIIINNNNNNN")
        print(len(self.states))
    
    def dfs(self):
        global opened 
        print('init_state (DFS)\n')
        print(self.init_state)
        while self.stack:
            self.current_state = self.stack.pop()
            if self.current_state.isGoal(' '):
                self.visited.append(deepcopy(self.current_state))
                print('Done\n')
                print(self.current_state)
                print(f"opened {opened}")
                return self.current_state
            if self.current_state not in self.visited:
                self.visited.append(self.current_state)
            stat = self.current_state.getNextStates(self , "DFS")
            for state in stat:
                if state not in self.visited:
                    self.stack.append(state)
                else:
                    print('visited')
        return None
    
    def bfs(self):
        global opened 
        print('init_state (BFS)\n')
        print(self.init_state)
        queue = deque([self.init_state])
        while queue:
            self.current_state = queue.popleft()
            if self.current_state.isGoal(' '):
                self.visited.append(deepcopy(self.current_state))
                print('Done\n')
                print(self.current_state)
                print(f"opened {opened}")
                return self.current_state
            if self.current_state not in self.visited:
                self.visited.append(self.current_state)
            stat = self.current_state.getNextStates(self , "BFS")
            for state in stat:
                if state not in self.visited and state not in queue:
                    queue.append(state)
                else:
                    print('visited')
        return None
    
    def ucs(self):
        global opened 
        print('init_state (UCS)\n')
        print(self.init_state)
        visited = []
        queue = PriorityQueue()
        queue.put(StateWrapper(self.current_state, 0)) 
        while not queue.empty():
            state_wrapper = queue.get() 
            self.current_state = state_wrapper.state
            if self.current_state.isGoal(' '):
                visited.append(deepcopy(self.current_state))
                print('Done\n')
                print(self.current_state)
                print(f"opened {opened}")
                return self.current_state
            if self.current_state not in visited:
                visited.append(self.current_state)
            stats = self.current_state.getNextStates(self, "UCS")
            for stat in stats:
                next_state, next_cost = stat[0][0], stat[0][1] 
                if next_state not in visited: 
                    queue.put(StateWrapper(next_state, next_cost)) 
                else:
                    print("visited")
        return None
    
    def heuristic_fn(self , state):
        cords = state.getCords()
        cords 
        if state.ballsrow.any() and state.basketrow.any() :
            if len(state.ballsrow) > 1 :
                xBall_2 = state.ballsrow[1] 
                yBall_2 = state.ballscol[1]
                
                xBall = state.ballsrow[0] 
                yBall = state.ballscol[0] 
                
                xBasket = state.basketrow[0] 
                yBasket = state.basketcol[0]
                
                manhatin_1 = abs(xBall - xBasket) + abs(yBall - yBasket)
                manhatin_2 = abs(xBall_2 - xBasket) + abs(yBall_2 - yBasket)
                
                if manhatin_2 < manhatin_1 :
                    return manhatin_2
                else:
                    return manhatin_1
            else :
                xBall = state.ballsrow[0] 
                yBall = state.ballscol[0] 
                
                xBasket = state.basketrow[0] 
                yBasket = state.basketcol[0]
                
                return abs(xBall - xBasket) + abs(yBall - yBasket)
        else :
            return 0
    
    #! not ready A*:
    def a_star(self):
        global opened
        print('init_state (A*)\n')
        print(self.init_state)
        visited = []
        queue = PriorityQueue() 
        heuristic_fn = self.heuristic_fn
        queue.put(StateWrapper_A_star(self.current_state, 0, heuristic_fn(self.current_state))) 
        while not queue.empty():
            state_wrapper = queue.get()  
            self.current_state = state_wrapper.state
            if self.current_state.isGoal(' '):
                visited.append(deepcopy(self.current_state))
                print('Done\n')
                print(self.current_state)
                print(f"opened {opened}")
                return self.current_state
            if self.current_state not in visited:
                visited.append(self.current_state)
            stats = self.current_state.getNextStates(self, "UCS")
            for stat in stats:
                next_state, next_cost = stat[0][0], stat[0][1]
                if next_state not in visited:
                    heuristic = heuristic_fn(next_state)
                    queue.put(StateWrapper_A_star(next_state, next_cost, heuristic))  
                    # print(next_state)
                else:
                    print("visited")
        return None
    
    def hill_climbing(self):
        global opened
        print('init_state (Hill Climbing)\n')
        print(self.init_state)
        visited = []
        while True:
            visited.append(self.current_state)  
            best_state = None
            best_heuristic = float('inf')
            stats = self.current_state.getNextStates(self, "UCS")
            for stat in stats:
                next_state, next_cost = stat[0][0], stat[0][1]
                heuristic = self.heuristic_fn(next_state)
                if heuristic < best_heuristic:
                    best_state = next_state
                    best_heuristic = heuristic
            if best_state is None or self.heuristic_fn(best_state) >= self.heuristic_fn(self.current_state):
                if self.current_state.isGoal(' '):
                    print('Done\n')
                    print(self.current_state)
                    print(f"opened {opened}")
                    return self.current_state
                else:
                    continue
            self.current_state = best_state
    
    def move(self , dirct) :
        self.init_state.balls_cords , self.init_state.basket_cords , self.init_state.coins_cords , self.init_state.box_cords = self.current_state.getCords()
        
        if dirct == 'right' :
            x , y = 0 , 1
    
        elif dirct == 'left' :
            x , y = 0 , -1
    
        elif dirct == 'up' :
            x , y = -1 , 0
    
        elif dirct == 'down' :
            x , y = 1 , 0
        else :
            return 0
        self.final_x , self.final_y = x , y
        
        #! moves section
        
        self.final_basket_move()
        self.final_balls_move()
        self.final_coin_move()
        self.final_box_move()
    
    #! move balls
    def moveBalls(self , x , y ) :
        # up down
        new_balls_row = self.current_state.ballsrow + x
        # right left
        new_balls_col = self.current_state.ballscol + y 
        return new_balls_row , new_balls_col
    
    def final_balls_move (self) :
        global costUSC
        new_balls_row = []
        new_balls_col = []
        for i in range(len(self.current_state.balls_cords)):
            new_x = self.current_state.balls_cords[i]['row'] + self.final_x
            new_y = self.current_state.balls_cords[i]['col'] + self.final_y
            if self.current_state.isVaildMove(new_x, new_y) :
                costUSC += 1
                balls_row, balls_col = self.moveBalls(self.final_x, self.final_y)
                new_balls_row.append(balls_row[i])
                new_balls_col.append(balls_col[i])
                self.current_state.board[self.current_state.balls_cords[i]['row']][self.current_state.balls_cords[i]['col']].type = CellType.EMPTY
                if len(new_balls_row) == 1 :
                    self.current_state.board[new_balls_row[0]][new_balls_col[0]].type = CellType.BALL
                elif len(new_balls_row) > 1 :
                    for j in range(len(new_balls_row)):
                        self.current_state.board[new_balls_row[j]][new_balls_col[j]].type = CellType.BALL
        return new_balls_row, new_balls_col
    
    #! move basket
    def moveBasket(self , x , y ) :
        # up and down
        new_basket_row = self.current_state.basketrow + x
        # right left
        new_basket_col = self.current_state.basketcol + y 
        return new_basket_row , new_basket_col
    
    def final_basket_move (self) :
        # global costUSC
        new_basket_row = []
        new_basket_col = []
        for i in range(len(self.current_state.basket_cords) ):
            new_x = self.init_state.basket_cords[i]['row'] + self.final_x
            new_y = self.init_state.basket_cords[i]['col'] + self.final_y
            if self.current_state.isVaildMove(new_x, new_y ) :
                # costUSC += 1
                basket_row , basket_col = self.moveBasket (self.final_x, self.final_y)
                new_basket_row.append(basket_row[i])
                new_basket_col.append(basket_col[i])
                self.current_state.board[self.current_state.basket_cords[i]['row']][self.current_state.basket_cords[i]['col']].type = CellType.EMPTY
                if len(new_basket_row) == 1 :
                    self.current_state.board[new_basket_row[0]][new_basket_col[0]].type = CellType.BASKET
                elif len(new_basket_row) > 1 :
                    for j in range(len(new_basket_row)):
                        self.current_state.board[new_basket_row[j]][new_basket_col[j]].type = CellType.BASKET
        return new_basket_row , new_basket_col
    
    #! move coin
    def moveCoin(self , x , y ) :
        # up and down
        new_coin_row = self.current_state.coinrow + x
        # right left
        new_coin_col = self.current_state.coincol + y 
        return new_coin_row , new_coin_col
    
    def final_coin_move (self) :
        # global costUSC
        new_coin_row = []
        new_coin_col = []
        for i in range(len(self.current_state.coins_cords)):
            new_x = self.current_state.coins_cords[i]['row'] + self.final_x
            new_y = self.current_state.coins_cords[i]['col'] + self.final_y
            if self.current_state.isVaildMove (new_x, new_y ) :
                # costUSC += 1
                coin_row , coin_col = self.moveCoin (self.final_x, self.final_y)
                new_coin_row.append(coin_row[i])
                new_coin_col.append(coin_col[i])
                self.current_state.board[self.current_state.coins_cords[i]['row']][self.current_state.coins_cords[i]['col']].type = CellType.EMPTY
                if len(new_coin_row) == 1 :
                    self.current_state.board[new_coin_row[0]][new_coin_col[0]].type = CellType.COIN
                elif len(new_coin_row) > 1 :
                    for j in range(len(new_coin_row)):
                        self.current_state.board[new_coin_row[j]][new_coin_col[j]].type = CellType.COIN
        return new_coin_row , new_coin_col
    
    #! move box
    def moveBox(self , x , y ) :
        # up and down
        new_box_row = self.current_state.boxrow + x
        # right left
        new_box_col = self.current_state.boxcol + y
        return new_box_row , new_box_col
    
    def final_box_move (self) :
        # global costUSC
        new_box_row = []
        new_box_col = []
        for i in range(len(self.current_state.box_cords)):
            new_x = self.current_state.box_cords[i]["row"] + self.final_x
            new_y = self.current_state.box_cords[i]["col"] + self.final_y
            if self.current_state.isVaildMove (new_x, new_y ) :
                # costUSC += 1
                box_row , box_col = self.moveBox (self.final_x, self.final_y)
                new_box_row.append(box_row[i])
                new_box_col.append(box_col[i])
                self.current_state.board[self.current_state.box_cords[i]['row']][self.current_state.box_cords[i]['col']].type = CellType.EMPTY
                if len(new_box_row) == 1 :
                    self.current_state.board[new_box_row[0]][new_box_col[0]].type = CellType.BOX
                elif len(new_box_row) > 1 :
                    for j in range(len(new_box_row)):
                        self.current_state.board[new_box_row[j]][new_box_col[j]].type = CellType.BOX
            
        return new_box_row , new_box_col
    
    def checkMoves(self, x, y):
        moves = []
        directions = []

        # Down
        if x + 1 < self.current_state.rows and self.current_state.board[x + 1, y].type == CellType.EMPTY:
            moves.append({'row': x + 1, 'col': y})
            directions.append('down')

        # Up
        if x - 1 >= 0 and self.current_state.board[x - 1, y].type == CellType.EMPTY:
            moves.append({'row': x - 1, 'col': y})
            directions.append('up')

        # Left
        if y - 1 >= 0 and self.current_state.board[x, y - 1].type == CellType.EMPTY:
            moves.append({'row': x, 'col': y - 1})
            directions.append('left')

        # Right
        if y + 1 < self.current_state.cols and self.current_state.board[x, y + 1].type == CellType.EMPTY:
            moves.append({'row': x, 'col': y + 1})
            directions.append('right')

        return np.array(directions) # moves ,

def main() :
    #* test user input
    def get_user_int_input():
        while True:
            x = input("1- user: \n2- DFS: \n3- BFS: \n4- UCS: \n5- A*: \n6- hill-climbing: \n")
            try:
                return int(x)
            except ValueError:
                print("Invalid input. Please enter a number.")
    #! LEVELS
    level_1_47 = np.array([
        [CellType.BALL,   CellType.BALL ,  CellType.BASKET ,    CellType.BALL     ],
        [CellType.EMPTY,    CellType.BOX ,  CellType.BOX ,   CellType.EMPTY       ],
        [CellType.EMPTY,     CellType.WALL ,  CellType.EMPTY ,    CellType.EMPTY  ],
        [CellType.EMPTY,  CellType.EMPTY ,  CellType.EMPTY,    CellType.BOX       ],
    ])
    
    level_2_26 = np.array([
        [CellType.WALL,   CellType.WALL ,  CellType.EMPTY ,    CellType.WALL , CellType.WALL],
        [CellType.WALL,   CellType.BALL ,  CellType.BASKET ,    CellType.BALL , CellType.WALL],
        [CellType.EMPTY,   CellType.EMPTY ,  CellType.WALL ,    CellType.EMPTY , CellType.EMPTY],
        [CellType.WALL,   CellType.EMPTY ,  CellType.BOX ,    CellType.EMPTY , CellType.WALL],
        [CellType.WALL,   CellType.WALL ,  CellType.EMPTY ,    CellType.WALL , CellType.WALL],
    ])
    
    level_3_25 = np.array([
        [CellType.COIN,   CellType.WALL ,  CellType.EMPTY ,    CellType.EMPTY],
        [ CellType.EMPTY,    CellType.EMPTY ,  CellType.EMPTY ,    CellType.EMPTY ],
        [CellType.EMPTY,     CellType.WALL ,  CellType.WALL ,    CellType.EMPTY  ],
        [CellType.BOX,  CellType.EMPTY ,  CellType.EMPTY,    CellType.EMPTY ],
        [CellType.BALL,  CellType.EMPTY ,  CellType.WALL,    CellType.BASKET ],
    ])
    
    level_4_35 = np.array([
        [CellType.BASKET,   CellType.EMPTY ,  CellType.EMPTY ,    CellType.BOX ,  CellType.WALL   ],
        [CellType.EMPTY,    CellType.EMPTY ,  CellType.WALL ,     CellType.COIN , CellType.WALL   ],
        [CellType.WALL,     CellType.EMPTY ,  CellType.EMPTY ,    CellType.WALL , CellType.BALL   ],
        [CellType.EMPTY,    CellType.EMPTY ,  CellType.EMPTY ,    CellType.EMPTY, CellType.EMPTY  ],
        [CellType.EMPTY,    CellType.WALL ,   CellType.EMPTY ,    CellType.WALL , CellType.WALL   ],
        [CellType.EMPTY,   CellType.EMPTY ,  CellType.EMPTY ,    CellType.BALL ,  CellType.WALL   ],
    ])
    
    level_5_30 = np.array([
        [CellType.WALL,   CellType.EMPTY ,  CellType.EMPTY ,    CellType.EMPTY , CellType.EMPTY],
        [CellType.EMPTY,   CellType.EMPTY ,  CellType.WALL ,    CellType.EMPTY , CellType.EMPTY],
        [CellType.EMPTY,   CellType.EMPTY ,  CellType.WALL ,    CellType.EMPTY , CellType.WALL],
        [CellType.WALL,   CellType.BASKET ,  CellType.EMPTY ,    CellType.EMPTY , CellType.WALL],
        [CellType.WALL,   CellType.WALL ,  CellType.BALL ,    CellType.BALL , CellType.BALL],
    ])
    # hill-climbing 
    level_6_34 = np.array([
        [CellType.EMPTY,   CellType.EMPTY ,  CellType.WALL ,    CellType.EMPTY , CellType.EMPTY],
        [CellType.WALL,   CellType.EMPTY ,  CellType.EMPTY ,    CellType.EMPTY , CellType.EMPTY],
        [CellType.EMPTY,   CellType.EMPTY ,  CellType.WALL ,    CellType.BASKET , CellType.WALL],
        [CellType.EMPTY,   CellType.EMPTY ,  CellType.WALL ,    CellType.COIN , CellType.EMPTY],
        [CellType.WALL,   CellType.EMPTY ,  CellType.EMPTY ,    CellType.BALL , CellType.EMPTY],
        [CellType.WALL,   CellType.BALL ,  CellType.WALL ,    CellType.WALL , CellType.EMPTY],
    ])
    
    level_7_40 = np.array([
        [CellType.EMPTY,   CellType.EMPTY ,  CellType.EMPTY ,    CellType.EMPTY , CellType.EMPTY],
        [CellType.EMPTY,   CellType.WALL ,  CellType.BASKET ,    CellType.EMPTY , CellType.BALL],
        [CellType.WALL,   CellType.EMPTY ,  CellType.EMPTY ,    CellType.EMPTY , CellType.WALL],
        [CellType.EMPTY,   CellType.EMPTY ,  CellType.BOX ,    CellType.WALL , CellType.EMPTY],
        [CellType.WALL,   CellType.EMPTY ,  CellType.BALL ,    CellType.EMPTY , CellType.EMPTY],
    ])
    
    level_8_43 = np.array([
        [CellType.EMPTY,   CellType.EMPTY ,  CellType.BALL ,    CellType.EMPTY],
        [CellType.WALL,    CellType.EMPTY ,  CellType.EMPTY ,   CellType.BALL ],
        [CellType.BOX,     CellType.EMPTY ,  CellType.WALL ,    CellType.BOX  ],
        [CellType.BASKET,  CellType.EMPTY ,  CellType.EMPTY,    CellType.COIN ],
    ])
    
    # ucs
    level_9_46 = np.array([
        [CellType.WALL,   CellType.EMPTY ,  CellType.BALL ,    CellType.WALL],
        [CellType.EMPTY,    CellType.EMPTY ,  CellType.EMPTY ,   CellType.BOX ],
        [CellType.EMPTY,     CellType.EMPTY ,  CellType.EMPTY ,    CellType.BOX  ],
        [CellType.EMPTY,  CellType.COIN ,  CellType.WALL,    CellType.BASKET ],
    ])
    
    level_10_44 = np.array([
        [CellType.WALL,   CellType.EMPTY ,  CellType.EMPTY ,    CellType.EMPTY],
        [CellType.BOX,    CellType.EMPTY ,  CellType.EMPTY ,   CellType.EMPTY ],
        [CellType.EMPTY,     CellType.EMPTY ,  CellType.EMPTY ,    CellType.EMPTY  ],
        [CellType.COIN,  CellType.BALL ,  CellType.BASKET,    CellType.BOX ],
    ])
    
    # A*
    level_11_49 = np.array([
        [CellType.EMPTY,   CellType.EMPTY ,  CellType.WALL ,    CellType.BASKET],
        [CellType.EMPTY,    CellType.BOX ,  CellType.BALL ,   CellType.COIN ],
        [CellType.EMPTY,     CellType.EMPTY ,  CellType.WALL ,    CellType.EMPTY  ],
        [CellType.EMPTY,  CellType.EMPTY ,  CellType.EMPTY,    CellType.EMPTY ],
    ])
    
    # UCS  A*
    level_12_41 = np.array([
        [CellType.WALL,   CellType.EMPTY ,  CellType.EMPTY ,    CellType.EMPTY],
        [CellType.EMPTY,    CellType.BALL ,  CellType.EMPTY ,   CellType.WALL ],
        [CellType.WALL,     CellType.BOX ,  CellType.EMPTY ,    CellType.EMPTY  ],
        [CellType.EMPTY,  CellType.BASKET ,  CellType.EMPTY,    CellType.EMPTY ],
    ])
    
    # UCS A* hill-climbing
    level_13_48 = np.array([
        [CellType.EMPTY,   CellType.WALL ,  CellType.EMPTY ,    CellType.EMPTY],
        [CellType.EMPTY,    CellType.EMPTY ,  CellType.EMPTY ,   CellType.EMPTY ],
        [CellType.COIN,     CellType.WALL ,  CellType.EMPTY ,    CellType.EMPTY  ],
        [CellType.BOX,  CellType.BASKET ,  CellType.BALL,    CellType.WALL ],
    ])
    
    level_14_51 = np.array([
        [CellType.EMPTY,   CellType.EMPTY ,  CellType.EMPTY ,    CellType.EMPTY],
        [CellType.EMPTY,    CellType.BASKET ,  CellType.BOX ,   CellType.BALL ],
        [CellType.EMPTY,     CellType.WALL ,  CellType.WALL ,    CellType.EMPTY  ],
        [CellType.EMPTY,  CellType.BALL ,  CellType.BALL,    CellType.EMPTY ],
        [CellType.EMPTY,  CellType.EMPTY ,  CellType.EMPTY,    CellType.EMPTY ],
    ])
    
    level_15_53 = np.array([
        [CellType.EMPTY,   CellType.WALL ,  CellType.WALL ,    CellType.EMPTY],
        [CellType.EMPTY,    CellType.BASKET ,  CellType.EMPTY ,   CellType.EMPTY ],
        [CellType.EMPTY,     CellType.COIN ,  CellType.EMPTY ,    CellType.EMPTY  ],
        [CellType.EMPTY,  CellType.BOX ,  CellType.EMPTY,    CellType.EMPTY ],
        [CellType.BALL,  CellType.WALL ,  CellType.WALL,    CellType.BALL ],
    ])
    
    init_board = level_13_48
    
    rows = len(init_board)
    cols = len(init_board[0])
    board = np.empty((rows,cols) , dtype = Cell)
    for i in range(rows):
        for j in range(cols):
            cell_type = CellType(init_board[i][j].value)
            
            board[i][j] = Cell( i , j ,  cell_type )
    init_state = State(rows , cols , board)
    
    print('init_state')
    print(init_state)
    print("__________________________")
    
    x = get_user_int_input()
    Game(init_state , int(x))

if __name__ == '__main__' :
    main()
