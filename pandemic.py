import pygame
import random
import math
from matplotlib import pyplot
pygame.init()

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

COLOR_DEFINITIONS = {
    "grey": (35, 35, 40),
    "light_grey": (70, 70, 90), 
    "white": (255, 248, 240),
    "red": (239, 71, 111),
    "blue": (17, 138, 178)
}

COLORS = {
    "background": COLOR_DEFINITIONS["grey"],
    "healthy": COLOR_DEFINITIONS["white"],
    "infected": COLOR_DEFINITIONS["red"],
    "immune": COLOR_DEFINITIONS["blue"],
    "dead": COLOR_DEFINITIONS["grey"]
}

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.people = []
    
    def get_neighbours(self, n_rows, n_cols):
        index = self.row * n_cols + self.col
        N = index - n_cols if index - n_cols >= 0 else None
        S = index + n_cols if index + n_cols < n_rows * n_cols else None
        E = index + 1 if (index + 1) % n_cols != 0 else None
        W = index - 1 if index % n_cols != 0 else None
        NE = N + 1 if N is not None and (N + 1) % n_cols != 0 else None
        NW = N - 1 if N is not None and N % n_cols != 0 else None
        SE = S + 1 if S is not None and (S + 1) % n_cols != 0 else None
        SW = S - 1 if S is not None and S % n_cols != 0 else None
        return [i for i in [index, N, S, E, W, NE, NW, SE, SW] if i is not None] 

class Grid:
    def __init__(self, people, h_size=20, v_size=20):
        self.h_size = h_size
        self.v_size = v_size
        self.n_rows = HEIGHT // v_size
        self.n_cols = WIDTH // h_size
        self.cells = []
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                self.cells.append(Cell(row, col))

        self.store_people(people)

    def store_people(self, people):
        for p in people:
            row = math.floor(p.y / self.v_size)
            col = math.floor(p.x / self.h_size)
            index = row * self.n_cols + col
            self.cells[index].people.append(p)

    def show(self, width=1):
        for c in self.cells:
            x = c.col * self.h_size
            y = c.row * self.v_size
            rect = pygame.Rect(x, y, self.h_size, self.v_size)
            pygame.draw.rect(SCREEN, COLOR_DEFINITIONS["light_grey"], rect, width=width)

class Person:
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.dx = 0
        self.dy = 0
        self.state = "healthy"
        self.recovery_counter = 0
        self.immunity_counter = 0 

    
    def show(self, size = 10):
        pygame.draw.circle(SCREEN, COLORS[self.state], (self.x, self.y), size)

    def move(self, speed = 0.005):

        # adjust position vector
        self.x += self.dx
        self.y += self.dy

        # avoid going out of bounds
        if self.x >= WIDTH or self.x <= 0:
            if self.x <= 0:
                self.x = 1
            elif self.x >= WIDTH:
                self.x = WIDTH - 1
            self.dx *= -1
            
        if self.y >= HEIGHT or self.y <= 0:
            if self.y <= 0:
                self.y = 1
            elif self.y >= HEIGHT:
                self.y = HEIGHT - 1
            self.dy *= -1

        # adjust velocity vector
        self.dx += random.uniform(-speed, speed)
        self.dy += random.uniform(-speed, speed)
        
    def get_infected(self, value = 2000):
        self.state = "infected"
        self.recovery_counter = value

    def recover(self, value= 1000):
        self.recovery_counter -= 1
        if self.recovery_counter == 0:
            self.state = "immune"
            self.immunity_counter = value

    def lose_immunity(self):
        self.immunity_counter -= 1
        if self.immunity_counter == 0:
            self.state = "healthy"
    
    def die(self, probability = 0.0001):
        if random.uniform(0,1) < probability:
            self.state = "dead"


class Pandemic:
    def __init__(
            self,
            n_people = 1000,
            size = 3,
            speed = 0.01,
            infect_dist = 5,
            recover_time = 500,
            immune_time = 1000,
            prob_catch = 0.01,
            prob_death = 0.0005
    ):
    
        self.people = [Person() for i in range(n_people)]
        self.size = size 
        self.speed = speed
        self.infect_dist = infect_dist
        self.recover_time = recover_time
        self.immune_time = immune_time
        self.prob_catch = prob_catch
        self.prob_death = prob_death
        self.grid = Grid(self.people)
        self.people[0].get_infected(recover_time)
        self.record = []
        self.over = False


    def update_grid(self):
        self.grid = Grid(self.people)
    
    def bad_infect_people(self):
        # infect other people
        for p in self.people:
            if p.state == "infected":
                for other in self.people:
                    if other.state == "healthy":
                        distance = ((p.x - other.x)**2 + (p.y - other.y)**2)**0.5
                        if distance < self.infect_dist:
                            other.get_infected(self.recover_time)
    def infect_people(self):
        for c in self.grid.cells:

            # move if nobody is infected
            states = [p.state for p in c.people]
            if "infected" not in states:
                continue
            
            # create list of all infected and healthy people in area
            people_in_area = []
            for index in c.get_neighbours(self.grid.n_rows, self.grid.n_cols):
                people_in_area += self.grid.cells[index].people
                infected_people = [p for p in people_in_area if p.state == "infected"]
                healthy_people = [p for p in people_in_area if p.state == "healthy"]

                if len(healthy_people) == 0:
                    continue
                
                # loop through infected people and infect healthy people
                for i in infected_people:
                    for h in healthy_people:
                        distance = ((i.x - h.x)**2 + (i.y - h.y)**2)**0.5
                        if distance < self.infect_dist:
                            if random.uniform(0,1) < self.prob_catch:
                                h.get_infected(self.recover_time)

    def run(self):
        self.update_grid()
        self.infect_people()

        for p in self.people:
            if p.state == "infected":
                p.die(self.prob_death)
                p.recover(self.immune_time)
            elif p.state == "immune":
                p.lose_immunity() 

            p.move(self.speed)
            p.show(self.size)

    def keep_track(self):
        states = [p.state for p in self.people]
        n_infected = states.count("infected")
        n_dead = states.count("dead")

        self.record.append([n_infected, n_dead])

        if n_infected == 0:
            self.over = True
    
    def summarize(self):
        time_index = range(1,len(self.record)+1)
        infected = [r[0] for r in self.record]
        dead = [r[1] for r in self.record]

        fig, ax = pyplot.subplots()
        ax.plot(time_index, infected, color="red")
        ax.set_xlabel("Period") 
        ax.set_ylabel("People Currently Infected", color="red")
        
        ax2 = ax.twinx()
        ax2.plot(time_index, dead, color = "black")
        ax2.set_ylabel("Cumulative Death Count", color="black")
        pyplot.show()



pandemic = Pandemic()

# pygame loop
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
animation = True
pausing = False

while animation and not pandemic.over:

    if not pausing:
        # pygame draws to screen
        # set bg color
        SCREEN.fill(COLORS["background"])

        # run pandemic and keep track
        pandemic.run()
        pandemic.keep_track()


        # update display and the clock
        clock.tick()
        clock_string = str(math.floor(clock.get_fps()))
        text = font.render(clock_string, True, COLOR_DEFINITIONS["blue"], COLORS["background"])
        text_box = text.get_rect(topleft = (10, 10))
        SCREEN.blit(text, text_box)
        pygame.display.flip()

    # track user interaction

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # user closes the window
            if event.type == pygame.QUIT:
                animation = False 
            
        # user presses a key
        if event.type == pygame.KEYDOWN:  
            # escape key close window
            if event.key == pygame.K_ESCAPE:
                animation = False
            # return key restart pandemic
            elif event.key == pygame.K_RETURN:
                pausing = False
                pandemic = Pandemic()
            
            # space (un)pause
            elif event.key == pygame.K_SPACE:
                pausing = not pausing


# create summary plot of pandemic
pandemic.summarize() 