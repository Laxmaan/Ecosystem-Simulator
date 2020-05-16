"""
Move with a Sprite Animation

Simple program to show basic sprite usage.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_move_animation
"""
import arcade
import random
import os
import numpy as np
import pymunk

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
WORLD_WIDTH = 6144
WORLD_HEIGHT = 3456
WALL_MARGIN = 128
SCREEN_TITLE = "Move with a Sprite Animation Example"



PLAYER_COUNT = 4
COIN_SCALE = 0.5
COIN_COUNT = 50
CHARACTER_SCALING = 1
VISION_RADIUS = 350
MOVEMENT_SPEED = 8
UPDATES_PER_FRAME = 7
SCROLL_SPEED = 25
FRICTION = -0.002

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, mirrored=True)
    ]


class PlayerCharacter(arcade.Sprite):
    def __init__(self,view):

        # Set up parent class
        super().__init__()
        # Register the calling view
        self.view = view
        self.physics_engine = arcade.PhysicsEngineSimple(self, self.view.wall_list)
        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        # Track out state
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False
        self.scale = CHARACTER_SCALING
        self.vision_radius = VISION_RADIUS
        self.strategy = "RANDOM"
        self.acceleration = 0.3
        self.should_accelerate = True

        # Find food
        self.target = None

        # Adjust the collision box. Default includes too much empty space
        # side-to-side. Box is centered at sprite center, (0, 0)
        self.points = [[-22, -64], [22, -64], [22, 28], [-22, 28]]


        self.position = np.random.normal([SCREEN_WIDTH//2,SCREEN_HEIGHT//2],100.0)
        
        self.scale = 0.8
        self.counter = 0
        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3
        main_path = np.random.choice([":resources:images/animated_characters/female_adventurer/femaleAdventurer",
                                      ":resources:images/animated_characters/female_person/femalePerson",
                                      ":resources:images/animated_characters/male_person/malePerson",
                                      ":resources:images/animated_characters/male_adventurer/maleAdventurer",
                                      ":resources:images/animated_characters/zombie/zombie",
                                      ":resources:images/animated_characters/robot/robot"], 1)[0]

        # Load textures for idle standing
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")

        # Load textures for walking
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)


    def choose_target(self):
        visible_coins = self.view.get_visible_coins(self.position,self.vision_radius)
        
        if len(visible_coins) > 0:
            #choose from visible coins using a strategy
            ind = np.random.choice(visible_coins,1)[0]
            #print(visible_coins,ind)
            self.target = self.view.coin_list[ind]
            self.target.color = arcade.color.AIR_FORCE_BLUE
        



    def move_towards_target(self,ctr):
        # Check if someone else has beat you to the target
        if self.target not in self.view.coin_list:
            self.target = None
            print("No target")


        if self.target:
            # get position vector and normalize it
            s = np.array(self.target.position) - self.position
            dist = np.linalg.norm(s)
            
            s = s/ dist

            # get velocity
            v = np.array(self.velocity)
            # get acceleration vector along the position vector
            acc_radial = s # towards target
            acc_corrective = 0
            if np.linalg.norm(v) > 0:
                acc_corrective = s - v/np.linalg.norm(v)

            acc = acc_radial + acc_corrective
            acc = self.acceleration / np.linalg.norm(acc) * acc
            #accelerate until vmax
            
            v += acc 
    
            # accelerate in that direction
            clip = min(MOVEMENT_SPEED, np.linalg.norm(v))
            v = clip * v/np.linalg.norm(v)

            self.velocity = list(v)
            
            if arcade.check_for_collision(self,self.target):
                self.target = None

        else:

        # search for target
            if ctr==0:
                theta = np.random.uniform(high=2*np.pi)

                v = MOVEMENT_SPEED* np.array([np.cos(theta), np.sin(theta)])

                self.velocity = v
            self.choose_target()

    def on_update(self,delta_time = 1/60):
        self.physics_engine.update()

        if not self.target and len(self.view.coin_list) > 0:
            self.choose_target()
        
        self.move_towards_target(self.counter)

        self.counter = (self.counter+1)% 15

        
    def update_animation(self, delta_time: float = 1/60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture // UPDATES_PER_FRAME][self.character_face_direction]

class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()
        self.time_taken = 0
        self.score = 0

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        """
        Draw "Game over" across the screen.
        """
        
        arcade.set_viewport(0,800, 0,600)

        
        arcade.draw_text("Game Over", 240, 400, arcade.color.WHITE, 54)
        arcade.draw_text("Click to restart", 310, 300, arcade.color.WHITE, 24)

        time_taken_formatted = f"{round(self.time_taken, 2)} seconds"
        arcade.draw_text(f"Time taken: {time_taken_formatted}",
                         SCREEN_WIDTH/2,
                         200,
                         arcade.color.GRAY,
                         font_size=15,
                         anchor_x="center")

        output_total = f"Total Score: {self.score}"
        arcade.draw_text(output_total, 10, 10, arcade.color.WHITE, 14)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)
        pass
       

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        """
        Initializer
        """
        # Scroll
        self.view_bottom = self.view_left = 0
        self.scroll_up =False
        self.scroll_down =False
        self.scroll_left =False
        self.scroll_right =False
        self.viewport_width,self.viewport_height = SCREEN_WIDTH,SCREEN_HEIGHT

        # Sprite lists
        self.player_list = None
        self.coin_list = None
        self.wall_list = None

        # Set up the player
        self.score = 0
        self.player = None
        self.player_agent = None
        self.path_to_goal = None

        # to track the number of update calls
        self.counter = 0
        self.movex = 0
        self.movey = 0
        self.move_randomly = True
        self.target_coin = None
        self.time_taken = 0

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        # Set up the player
        self.score = 0        

        for _ in range(PLAYER_COUNT):
            self.player_list.append(PlayerCharacter(self))

        #bottom and top wall
        for x in range(-WALL_MARGIN , WORLD_WIDTH+WALL_MARGIN+1, 64):
            wall = arcade.Sprite(":resources:images/tiles/brickBrown.png", 0.5)
            wall.left = x 
            wall.bottom = -WALL_MARGIN
            self.wall_list.append(wall)

            wall = arcade.Sprite(":resources:images/tiles/brickBrown.png", 0.5)
            wall.left = x 
            wall.bottom = WORLD_HEIGHT + WALL_MARGIN
            self.wall_list.append(wall)

        # left and right walls
        for y in range(-WALL_MARGIN , WORLD_HEIGHT+WALL_MARGIN+1, 64):
            wall = arcade.Sprite(":resources:images/tiles/brickBrown.png", 0.5)
            wall.left = - WALL_MARGIN 
            wall.bottom = y
            self.wall_list.append(wall)

            wall = arcade.Sprite(":resources:images/tiles/brickBrown.png", 0.5)
            wall.left = WORLD_WIDTH + WALL_MARGIN
            wall.bottom = y
            self.wall_list.append(wall)

        

        for i in range(COIN_COUNT):
            coin = arcade.AnimatedTimeSprite(scale=0.5)
            
            coin.textures = []
            coin.textures.append(arcade.load_texture("./Sprites/Isometric/apple_NE.png"))
            coin.textures.append(arcade.load_texture("./Sprites/Isometric/apple_NW.png"))
            coin.textures.append(arcade.load_texture("./Sprites/Isometric/apple_SW.png"))
            coin.textures.append(arcade.load_texture("./Sprites/Isometric/apple_SE.png"))
            coin.scale = COIN_SCALE
            coin.cur_texture_index = random.randrange(len(coin.textures))
            coin.texture= coin.textures[coin.cur_texture_index]
            
            # Boolean variable if we successfully placed the coin
            coin_placed_successfully = False

            # Keep trying until success
            while not coin_placed_successfully:
                # Position the coin
                coin.center_x = random.randrange(WORLD_WIDTH)
                coin.center_y = random.randrange(WORLD_HEIGHT)

                # See if the coin is hitting a wall
                wall_hit_list = arcade.check_for_collision_with_list(coin, self.wall_list)

                # See if the coin is hitting another coin
                coin_hit_list = arcade.check_for_collision_with_list(coin, self.coin_list)

                if len(wall_hit_list) == 0 and len(coin_hit_list) == 0:
                    # It is!
                    coin_placed_successfully = True

            # Add the coin to the lists
            self.coin_list.append(coin)

            # --- END OF IMPORTANT PART ---
           
            #
            
            

        
        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):

        print(self.viewport_width,self.viewport_height)
        if scroll_y > 0: #zoom in
            self.viewport_width = int(max(self.viewport_width*0.8,960))
            self.viewport_height = int(max(self.viewport_height*0.8,540))

        elif scroll_y < 0: #zoom out
            self.viewport_width = int(min(self.viewport_width*1.2,WORLD_WIDTH+2*WALL_MARGIN))
            self.viewport_height = int(min(self.viewport_height*1.2,WORLD_HEIGHT+2*WALL_MARGIN))
        
        
        print(self.viewport_width,self.viewport_height)
        
        arcade.set_viewport(self.view_left,
                            self.viewport_width + self.view_left,
                            self.view_bottom,
                            self.viewport_height + self.view_bottom)

    def on_show(self):
        arcade.set_background_color(arcade.color.AMAZON)

        # Don't show the mouse cursor
        self.window.set_mouse_visible(True)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.coin_list.draw()
        self.player_list.draw()
        self.wall_list.draw()
        for player in self.player_list:
            arcade.draw_circle_outline(player.center_x,
                                       player.center_y,
                                       player.vision_radius,
                                       arcade.color.WHITE, 3)
        # Put the text on the screen.
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

        for coin in self.coin_list:
            arcade.draw_point(coin.center_x, coin.center_y, arcade.color.RED, 10)

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """
        if key in[arcade.key.UP, arcade.key.W] :
            #self.player.change_y = MOVEMENT_SPEED
            self.scroll_up = True
        if key in[arcade.key.DOWN, arcade.key.S]:
            #self.player.change_y = -MOVEMENT_SPEED
            self.scroll_down = True
        elif key in[arcade.key.LEFT, arcade.key.A]:
            self.scroll_left = True
        elif key in[arcade.key.RIGHT, arcade.key.D]:
            self.scroll_right = True
       
            
    #aw
        

    def on_key_release(self, key, modifiers):
        """
        Called when the user releases a key.
        """
        if key in[arcade.key.UP, arcade.key.W] :
            self.scroll_up = False
        elif key in[arcade.key.DOWN, arcade.key.S]:
            self.scroll_down = False
        elif key in[arcade.key.LEFT, arcade.key.A]:
            self.scroll_left = False
        elif key in[arcade.key.RIGHT, arcade.key.D]:
            self.scroll_right = False



    def get_visible_coins(self, position, vision_radius):
        visible_coins= []
        if len(self.coin_list) > 0:
            x,y = position
            pos = np.array([[c.center_x,c.center_y] for c in self.coin_list])
            dists = np.linalg.norm(pos - [x, y],axis=1)
            visible_coins = np.arange(len(self.coin_list))
            if vision_radius > 0:
                visible_coins = visible_coins[dists <= vision_radius]

        return visible_coins



    def on_update(self, delta_time):
        """ Movement and game logic """

        self.coin_list.update()
        self.coin_list.update_animation()
        self.player_list.on_update(delta_time)
        self.player_list.update_animation()

        


        width, height = self.window.get_size()
        if self.scroll_up ^ self.scroll_down:
            self.view_bottom += SCROLL_SPEED*(self.scroll_up - self.scroll_down)

        if self.scroll_left ^ self.scroll_right:
            self.view_left += SCROLL_SPEED*(self.scroll_right - self.scroll_left)


        arcade.set_viewport(self.view_left,
                            self.viewport_width + self.view_left,
                            self.view_bottom,
                            self.viewport_height + self.view_bottom)



        # Generate a list of all sprites that collided with the player.
        if len(self.coin_list) > 0:

            
            self.counter = (self.counter + 1) % 20
            hit_list = []
            for player in self.player_list:
                hit_list += arcade.check_for_collision_with_list(player, self.coin_list)
            
            for coin in hit_list:
                coin.remove_from_sprite_lists()
                print(coin in self.coin_list)
                self.score += 1

            self.time_taken += delta_time

            # Call update on all sprites (The sprites don't do much in this
            # example though.)
            self.coin_list.update()
            self.player_list.update()

            # Generate a list of all sprites that collided with the player.
            #hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

            # Loop through each colliding sprite, remove it, and add to the
            # score.
            #for coin in hit_list:
            #    coin.kill()
            #    self.score += 1
            #    self.window.total_score += 1

        
        else:
            game_over_view = GameOverView()
            game_over_view.time_taken = self.time_taken
            game_over_view.score = self.score
            self.window.set_mouse_visible(True)
            self.window.show_view(game_over_view)

    '''
    def on_mouse_motion(self, x, y, _dx, _dy):
        """
        Called whenever the mouse moves.
        """
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    '''


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE,fullscreen=False, resizable=True)
    window.maximize()
    
    gameview = GameView()
    gameview.setup()
    window.show_view(gameview)
    arcade.run()


if __name__ == "__main__":
    main()
