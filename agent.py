"""from queue import PriorityQueue
import numpy as np
class AStarPoint():
    def __init__(self,point, parent=None):
        self.x = int(point[0])
        self.y = int(point[1])
        self.parent = None
        self.f = -1
        self.g = -1
        self.h = -1

    def __str__(self):
        return f"({self.x}, {self.y})"

class Graph():
    def __init__(self):
        self.visited = set()
    
    def neighbors(self, current, max_x, max_y):
        u,v = current
        if current in self.visited:
            return []
        else:
            self.visited.add(current)
        rets=[]
        for x in range(3):
            for y in range(3):
                m = u+x-1
                n = v+y-1
                if 0 <= m <= max_x and 0 <= n <= max_y:
                    rets.append((m, n))
                    
                    
        return rets

    
    def cost(self,a,b):
        x1, y1 = a
        x2, y2 = b
        return abs(x1-x2) + abs(y1-y2)


class AStarAgent():
    def __init__(self, goals, root):
        self.goals = goals
        self.root = root
        self.open_list = set()
        self.closed_list = {}
        self.curr_goal_index = np.argmin([self.heuristic(goal, self.root)
                                         for goal in self.goals])
        self.curr_goal = self.goals[self.curr_goal_index]
        self.graph = Graph()




    def heuristic(self,a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2)+ abs(y1 - y2)

    def a_star_search(self, max_x, max_y):
        frontier = PriorityQueue()
        frontier.put(self.root, 0)
        came_from = {}
        cost_so_far = {}
        came_from[self.root] = None
        cost_so_far[self.root] = 0
        
        while not frontier.empty():
            current = frontier.get()
            
            if current == self.curr_goal:
                break
            
            for next in self.graph.neighbors(current, max_x, max_y):
                new_cost = cost_so_far[current] + self.graph.cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(self.curr_goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current
        
        #unravel the path
        current = self.curr_goal
        path =[]
        print(f"from :{self.root} to {self.curr_goal} ")
        #print(came_from)
        while current != self.root:
            #print(current)
            path.insert(0,current)
            current = came_from[current]
        
        return path, came_from, cost_so_far
    
"""