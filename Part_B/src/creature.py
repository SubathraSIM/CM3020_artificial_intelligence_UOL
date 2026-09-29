# Importing all the required library
import genome 
from xml.dom.minidom import getDOMImplementation
from enum import Enum
import numpy as np

class MotorType(Enum):
    # pulse wave output
    PULSE = 1
    # sine wave output
    SINE = 2

# Give the motor output each time
class Motor:
    def __init__(self, control_waveform, control_amp, control_freq, blend= False):
        if control_waveform <= 0.5:
            # use the pulse
            self.motor_type = MotorType.PULSE
        else:
            # use the sine
            self.motor_type = MotorType.SINE
        # how strong the motor
        self.amp = control_amp
        # how fast the motor
        self.freq = control_freq
        # motor phase 0
        self.phase = 0
        # waveform value
        self.waveform = control_waveform 
        # blend to combine both pulse and sine if true
        self.blend = blend
    
    # # Initial get_output function before the advanced part
    # def get_output(self):
    #     # move it forward and close around
    #     self.phase = (self.phase + self.freq) % (np.pi * 2)
    #     # if pulse type
    #     if self.motor_type == MotorType.PULSE:
    #         # If self.phase is more than np.pi
    #         if self.phase < np.pi:
    #             # output is equal 1
    #             output = 1
    #         else:
    #             # output equal to -1
    #             output = -1
    #     # if sine type
    #     if self.motor_type == MotorType.SINE:
    #         output = np.sin(self.phase)
    #     # return output
    #     return output 

    # get_output changed to include the blend version for the advanced part
    def get_output(self):
        # move it forward and close around
        self.phase = (self.phase + self.freq) % (np.pi * 2)
        # If not blend
        if not self.blend:
            # if pulse type
            if self.motor_type == MotorType.PULSE:
                # +1 for first hald, -1 for second
                output = 1 if self.phase < np.pi else -1
            else:
                # sine output
                output = np.sin(self.phase)
            # multiple by amp which is how strong the motor is
            return self.amp * output

        # blend amount
        wave_form = float(self.waveform)
        # pulse value
        pulse = 1 if self.phase < np.pi else -1
        # sine value
        sine = np.sin(self.phase)
        # mix value
        sin_pulsemixed = (1.0 - wave_form) * pulse + wave_form * sine
        # multiple by amp which is how strong the motor is
        return self.amp * sin_pulsemixed


class Creature:
    def __init__(self, gene_count):
        # gene specification
        self.spec = genome.Genome.get_gene_spec()
        # random dna with gene count
        self.dna = genome.Genome.get_random_genome(len(self.spec), gene_count)
        # flat links
        self.flat_links = None
        # expanded links
        self.exp_links = None
        # motor object
        self.motors = None
        # first position of the creature
        self.start_position = None
        # last position of the creature
        self.last_position = None
        # highest height reach
        self.max_height = None
        # for flying in the air
        self.airbornenumber = 0
        # creture goes out of the arena
        self.out_of_bounds = False
        # cheated 
        self.cheated = False
        # smallest distance to the centre
        self.min_radius = None
        # highest height reach near the mountain
        self.maxheightnear = None
        # previous position
        self.prev_pos = None
        # uphill movement start score
        self.uphill_score = 0.0
        # count steps
        self.near_steps = 0


    def get_flat_links(self):
        # if flat links none
        if self.flat_links == None:
            # change dna into gene dictionaries and into links objects
            gdicts = genome.Genome.get_genome_dicts(self.dna, self.spec)
            self.flat_links = genome.Genome.genome_to_links(gdicts)
        # return flat links
        return self.flat_links
    
    def get_expanded_links(self):
        # get flat links
        self.get_flat_links()
        # if expandaed links not none
        if self.exp_links is not None:
            # return expanded links
            return self.exp_links
        
        # expanded list root link
        exp_links = [self.flat_links[0]]
        # results into the expanded links
        genome.Genome.expandLinks(self.flat_links[0], 
                                self.flat_links[0].name, 
                                self.flat_links, 
                                exp_links)
        # save and return the expanded links
        self.exp_links = exp_links
        return self.exp_links

    def to_xml(self):
        # get the expanded links
        self.get_expanded_links()
        # create xml dom implementation
        domimpl = getDOMImplementation()
        # create xml
        adom = domimpl.createDocument(None, "start", None)
        # robot tag
        robot_tag = adom.createElement("robot")
        # add each link to robot
        for link in self.exp_links:
            robot_tag.appendChild(link.to_link_element(adom))
        # add joint elements skip the first one
        first = True
        for link in self.exp_links:
            if first:
                first = False
                continue
            robot_tag.appendChild(link.to_joint_element(adom))
        # robot name attribute
        robot_tag.setAttribute("name", "pepe")
        # urdf xml string
        return '<?xml version="1.0"?>' + robot_tag.toprettyxml()
    
    # Initial get_motors function before the advanced part
    # def get_motors(self):
    #     # get expanded links
    #     self.get_expanded_links()
    #     # create motors
    #     if self.motors == None:
    #         motors = []
    #         # create one motor per joint
    #         for i in range(1, len(self.exp_links)):
    #             l = self.exp_links[i]
    #             # motor use link control values
    #             m = Motor(l.control_waveform, l.control_amp,  l.control_freq)
    #             motors.append(m)
    #         self.motors = motors 
    #     return self.motors 
    
    def get_motors(self, blend=False):
        # get expanded links
        self.get_expanded_links()
        # create motors
        if self.motors is None:
            motors = []
            # create one motor per joint
            for i in range(1, len(self.exp_links)):
                l = self.exp_links[i]
                # motor use link control values using blend
                m = Motor(l.control_waveform, l.control_amp,  l.control_freq, blend=blend)
                motors.append(m)
            self.motors = motors
        return self.motors

    def update_position(self, pos):
        # x, y, z position
        x, y, z = pos

        # start values based on the first position
        if self.start_position is None:
            self.start_position = pos
            self.last_position = pos
            self.prev_pos = pos
            # tracking values
            self.max_height = z
            self.min_radius = float(np.sqrt(x*x + y*y))
            self.maxheightnear = None
            self.uphill_score = 0.0
            self.near_steps = 0
            return

        # update the last position.
        self.last_position = pos

        # radius from center
        radius = float(np.sqrt(x*x + y*y))

        # track the closest distance to center
        if self.min_radius is None or radius < self.min_radius:
            self.min_radius = radius

        # overall max height
        if self.max_height is None or z > self.max_height:
            self.max_height = z

        # creature is near the slope area, this step as near step.
        if radius <= 5.5:
            self.near_steps += 1

            # Tracking the highest height reached while near the mountain
            if self.maxheightnear is None or z > self.maxheightnear:
                self.maxheightnear = z

            # If have a previous position change in height
            if self.prev_pos is not None:
                height = float(z - self.prev_pos[2])
                if height > 0:
                    self.uphill_score += height

        # current position as before 
        self.prev_pos = pos
    
    def get_distance_travelled(self):
        # run is invalid or missing data, fitness 0
        if self.cheated or self.start_position is None or self.last_position is None:
            return 0.0

        # start position
        sx, sy, sz = self.start_position

        # last position
        lx, ly, lz = self.last_position

        # radius from the centre
        startradius = float(np.sqrt(sx*sx + sy*sy))

        # last radius from the centre
        lastradius = float(np.sqrt(lx*lx + ly*ly))

        # how much closer it moved to the centre
        progress = max(0.0, startradius - lastradius)

        # reward if it got the near slope
        if self.min_radius is None:
            close = 0.0
        else:
            close = max(0.0, 5.5 - float(self.min_radius))

        # best height gained near the mountain
        if self.maxheightnear is None:
            bestheightincrease = 0.0
        else:
            bestheightincrease = max(0.0, float(self.maxheightnear) - float(sz))

        # final height gained
        finalheight = max(0.0, float(lz) - float(sz))

        # conitnuous climb
        uphill = max(0.0, float(self.uphill_score))

        # rewards weightage
        W_BEST  = 100.0
        W_CLOSE  = 25.0
        W_UPHILL = 15.0
        W_FINAL = 20.0
        W_PROGRESS = 8.0

        # fitness score calculation
        fitness = (W_BEST  * bestheightincrease + W_FINAL * finalheight + W_UPHILL * uphill + W_PROGRESS * progress + W_CLOSE  * close)

        # does not return 0
        return max(1e-6, float(fitness))


    # update the dna
    def update_dna(self, dna):
        # replace creature dna
        self.dna = dna
        # clear cached links, motors
        self.flat_links = None
        self.exp_links = None
        self.motors = None
        # reset the positions
        self.start_position = None
        self.last_position = None
        # reset all the values
        self.max_height = None
        self.airbornenumber = 0
        self.out_of_bounds = False
        self.cheated = False
        self.min_radius = None
        self.maxheightnear = None
        self.prev_pos = None
        self.uphill_score = 0.0
        self.near_steps = 0