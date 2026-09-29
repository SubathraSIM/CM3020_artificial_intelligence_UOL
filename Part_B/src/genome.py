# Import the required library
import numpy as np
import copy 
import random

class Genome():
    @staticmethod 
    # one random gene value
    def get_random_gene(length):
        gene = np.array([np.random.random() for i in range(length)])
        return gene
    
    @staticmethod 
    # create genome
    def get_random_genome(gene_length, gene_count):
        genome = [Genome.get_random_gene(gene_length) for i in range(gene_count)]
        return genome

    @staticmethod
    # gene spec each gene value with scale number
    def get_gene_spec():
        gene_spec =  {"link-shape":{"scale":1}, 
            "link-length": {"scale":2},
            "link-radius": {"scale":1},
            "link-recurrence": {"scale":3},
            "link-mass": {"scale":1},
            "joint-type": {"scale":1},
            "joint-parent":{"scale":1},
            "joint-axis-xyz": {"scale":1},
            "joint-origin-rpy-1":{"scale":np.pi * 2},
            "joint-origin-rpy-2":{"scale":np.pi * 2},
            "joint-origin-rpy-3":{"scale":np.pi * 2},
            "joint-origin-xyz-1":{"scale":1},
            "joint-origin-xyz-2":{"scale":1},
            "joint-origin-xyz-3":{"scale":1},
            "control-waveform":{"scale":1},
            "control-amp":{"scale":0.25},
            "control-freq":{"scale":1}
            }
        # index number to each key
        ind = 0
        for key in gene_spec.keys():
            gene_spec[key]["ind"] = ind
            ind = ind + 1
        return gene_spec
    
    @staticmethod
    # change one gene array to dictionary using the spec with scaling
    def get_gene_dict(gene, spec):
        gdict = {}
        for key in spec:
            ind = spec[key]["ind"]
            scale = spec[key]["scale"]
            gdict[key] = gene[ind] * scale
        return gdict

    @staticmethod
    # convert the full genome into list of dictionary
    def get_genome_dicts(genome, spec):
        gdicts = []
        for gene in genome:
            gdicts.append(Genome.get_gene_dict(gene, spec))
        return gdicts

    @staticmethod
    # expand flat link list into full link tree
    def expandLinks(parent_link, uniq_parent_name, flat_links, exp_links):
        children = [l for l in flat_links if l.parent_name == parent_link.name]
        sibling_ind = 1
        for c in children:
            for r in range(int(c.recur)):
                sibling_ind  = sibling_ind +1
                # copy link to create repeated children
                c_copy = copy.copy(c)
                c_copy.parent_name = uniq_parent_name
                # give unique name
                uniq_name = c_copy.name + str(len(exp_links))
                c_copy.name = uniq_name
                c_copy.sibling_ind = sibling_ind
                # append to expanded links
                exp_links.append(c_copy)
                # check link cannot to itself
                assert c.parent_name != c.name, "Genome::expandLinks: link joined to itself: " + c.name + " joins " + c.parent_name 
                # expand links
                Genome.expandLinks(c, uniq_name, flat_links, exp_links)

    @staticmethod
    # covert gene dictionary to urdf object
    def genome_to_links(gdicts):
        links = []
        link_ind = 0
        # keep parent names links
        parent_names = [str(link_ind)]
        for gdict in gdicts:
            link_name = str(link_ind)
            # choose parent link base on the joint parent value
            parent_ind = gdict["joint-parent"] * len(parent_names)
            assert parent_ind < len(parent_names), "genome.py: parent ind too high: " + str(parent_ind) + "got: " + str(parent_names)
            parent_name = parent_names[int(parent_ind)]
            # control recurrence
            recur = gdict["link-recurrence"]
            # urdf link for the gene
            link = URDFLink(name=link_name, 
                            parent_name=parent_name, 
                            recur=recur+1, 
                            link_length=gdict["link-length"], 
                            link_radius=gdict["link-radius"], 
                            link_mass=gdict["link-mass"],
                            joint_type=gdict["joint-type"],
                            joint_parent=gdict["joint-parent"],
                            joint_axis_xyz=gdict["joint-axis-xyz"],
                            joint_origin_rpy_1=gdict["joint-origin-rpy-1"],
                            joint_origin_rpy_2=gdict["joint-origin-rpy-2"],
                            joint_origin_rpy_3=gdict["joint-origin-rpy-3"],
                            joint_origin_xyz_1=gdict["joint-origin-xyz-1"],
                            joint_origin_xyz_2=gdict["joint-origin-xyz-2"],
                            joint_origin_xyz_3=gdict["joint-origin-xyz-3"],
                            control_waveform=gdict["control-waveform"],
                            control_amp=gdict["control-amp"],
                            control_freq=gdict["control-freq"])
            links.append(link)
            # add link as a possible parent except the first link
            if link_ind != 0:
                parent_names.append(link_name)
            link_ind = link_ind + 1

        # now just fix the first link so it links to nothing
        links[0].parent_name = "None"
        return links

    @staticmethod
    def crossover(g1, g2):
        # create child genome concatenate 2 parent genome
        x1 = random.randint(0, len(g1)-1)
        x2 = random.randint(0, len(g2)-1)
        g3 = np.concatenate((g1[x1:], g2[x2:])) 
        # child length same as parent
        if len(g3) > len(g1):
            g3 = g3[0:len(g1)] 
        return g3

    # Initial point_mutate which was used for intial testing
    # @staticmethod
    # def point_mutate(genome, rate, amount):
    #     new_genome = copy.copy(genome)
    #     for gene in new_genome:
    #         for i in range(len(gene)):
    #             if random.random() < rate:
    #                 gene[i] += 0.1
    #             if gene[i] >= 1.0:
    #                 gene[i] = 0.9999
    #             if gene[i] < 0.0:
    #                 gene[i] = 0.0
    #     return new_genome

    # point_mutate changed for advanced part to inlcude the motors
    @staticmethod
    def point_mutate(genome, rate, amount, motor_only=False):
        # mutate gene values with random change
        new_genome = copy.copy(genome)
        motorindex = None
        if motor_only:
            # get gene spec
            spec = Genome.get_gene_spec()
            # indexs of motor genes 
            motorindex = {
                spec["control-waveform"]["ind"],
                spec["control-amp"]["ind"],
                spec["control-freq"]["ind"],
            }
        for gene in new_genome:
            for i in range(len(gene)):
                # skip body genes when motor_only is true
                if motorindex is not None and i not in motorindex:
                    continue
                # if random more than rate
                if random.random() < rate:
                    # create random change and add to gene value
                    randomchange = (random.random() - 0.5) * 2 * amount
                    gene[i] += randomchange
                # values stay between 0 and 1
                if gene[i] >= 1.0:
                    gene[i] = 0.9999
                if gene[i] < 0.0:
                    gene[i] = 0.0
        # return the new genome
        return new_genome

    @staticmethod
    def shrink_mutate(genome, rate):
        # randomly remove one gene to make the body smaller
        if len(genome) == 1:
            return copy.copy(genome)
        # if random more than rate
        if random.random() < rate:
            ind = random.randint(0, len(genome)-1)
            # delete the gene
            new_genome = np.delete(genome, ind, 0)
            return new_genome
        else:
            return copy.copy(genome)

    @staticmethod
    # randomly add one new gene to make the body bigger
    def grow_mutate(genome, rate):
        # if random more than rate
        if random.random() < rate:
            gene = Genome.get_random_gene(len(genome[0]))
            new_genome = copy.copy(genome)
            # add the gene
            new_genome = np.append(new_genome, [gene], axis=0)
            return new_genome
        else:
            return copy.copy(genome)


    @staticmethod
    def to_csv(dna, csv_file):
        # save dna to the csv file
        csv_str = ""
        for gene in dna:
            for val in gene:
                csv_str = csv_str + str(val) + ","
            csv_str = csv_str + '\n'
        # write mode of the csv file
        with open(csv_file, 'w') as f:
            f.write(csv_str)

    @staticmethod
    def from_csv(filename):
        # empty string
        csv_str = ''
        # open the csv file
        with open(filename) as f:
            csv_str = f.read()  
        # list to store the gene 
        dna = []
        # split by /n
        lines = csv_str.split('\n')
        # return as a list of genes
        for line in lines:
            vals = line.split(',')
            gene = [float(v) for v in vals if v != '']
            if len(gene) > 0:
                dna.append(gene)
        return dna

class URDFLink:
    # store one link and joint setting 
    def __init__(self, name, parent_name, recur, 
                link_length=0.1, 
                link_radius=0.1, 
                link_mass=0.1,
                joint_type=0.1,
                joint_parent=0.1,
                joint_axis_xyz=0.1,
                joint_origin_rpy_1=0.1,
                joint_origin_rpy_2=0.1,
                joint_origin_rpy_3=0.1,
                joint_origin_xyz_1=0.1,
                joint_origin_xyz_2=0.1,
                joint_origin_xyz_3=0.1,
                control_waveform=0.1,
                control_amp=0.1,
                control_freq=0.1):
        # store all link and joints
        self.name = name
        self.parent_name = parent_name
        self.recur = recur 
        self.link_length=link_length 
        self.link_radius=link_radius
        self.link_mass=link_mass
        self.joint_type=joint_type
        self.joint_parent=joint_parent
        self.joint_axis_xyz=joint_axis_xyz
        self.joint_origin_rpy_1=joint_origin_rpy_1
        self.joint_origin_rpy_2=joint_origin_rpy_2
        self.joint_origin_rpy_3=joint_origin_rpy_3
        self.joint_origin_xyz_1=joint_origin_xyz_1
        self.joint_origin_xyz_2=joint_origin_xyz_2
        self.joint_origin_xyz_3=joint_origin_xyz_3
        self.control_waveform=control_waveform
        self.control_amp=control_amp
        self.control_freq=control_freq
        # use to change angles
        self.sibling_ind = 1

    def to_link_element(self, adom):
        # urdf xml element
        link_tag = adom.createElement("link")
        link_tag.setAttribute("name", self.name)

        # visual shape
        vis_tag = adom.createElement("visual")
        geom_tag = adom.createElement("geometry")
        cyl_tag = adom.createElement("cylinder")
        cyl_tag.setAttribute("length", str(self.link_length))
        cyl_tag.setAttribute("radius", str(self.link_radius))
        geom_tag.appendChild(cyl_tag)
        vis_tag.appendChild(geom_tag)
        
        # collision shape
        coll_tag = adom.createElement("collision")
        c_geom_tag = adom.createElement("geometry")
        c_cyl_tag = adom.createElement("cylinder")
        c_cyl_tag.setAttribute("length", str(self.link_length))
        c_cyl_tag.setAttribute("radius", str(self.link_radius))
        c_geom_tag.appendChild(c_cyl_tag)
        coll_tag.appendChild(c_geom_tag)

        # Inertial values
        inertial_tag = adom.createElement("inertial")
        mass_tag = adom.createElement("mass")
        # pi r^2 * height
        mass = np.pi * (self.link_radius * self.link_radius) * self.link_length
        mass_tag.setAttribute("value", str(mass))
        inertia_tag = adom.createElement("inertia")
        inertia_tag.setAttribute("ixx", "0.03")
        inertia_tag.setAttribute("iyy", "0.03")
        inertia_tag.setAttribute("izz", "0.03")
        inertia_tag.setAttribute("ixy", "0")
        inertia_tag.setAttribute("ixz", "0")
        inertia_tag.setAttribute("iyx", "0")
        inertial_tag.appendChild(mass_tag)
        inertial_tag.appendChild(inertia_tag)
        
        # attach all section to the link tag
        link_tag.appendChild(vis_tag)
        link_tag.appendChild(coll_tag)
        link_tag.appendChild(inertial_tag)
        
        # return link tag
        return link_tag

    def to_joint_element(self, adom):
        # create urdf xml element
        joint_tag = adom.createElement("joint")
        joint_tag.setAttribute("name", self.name + "_to_" + self.parent_name)
        
        # joint type is revolute
        if self.joint_type >= 0.5:
            joint_tag.setAttribute("type", "revolute")
        else:
            joint_tag.setAttribute("type", "revolute")
        
        # parent and child links
        parent_tag = adom.createElement("parent")
        parent_tag.setAttribute("link", self.parent_name)
        child_tag = adom.createElement("child")
        child_tag.setAttribute("link", self.name)
        
        #rotation axis based on join axis xyz
        axis_tag = adom.createElement("axis")
        if self.joint_axis_xyz <= 0.33:
            axis_tag.setAttribute("xyz", "1 0 0")
        if self.joint_axis_xyz > 0.33 and self.joint_axis_xyz <= 0.66:
            axis_tag.setAttribute("xyz", "0 1 0")
        if self.joint_axis_xyz > 0.66:
            axis_tag.setAttribute("xyz", "0 0 1")
        
        # joint limits
        limit_tag = adom.createElement("limit")
        # effort upper lower velocity
        limit_tag.setAttribute("effort", "1")
        limit_tag.setAttribute("upper", "-3.1415")
        limit_tag.setAttribute("lower", "3.1415")
        limit_tag.setAttribute("velocity", "1")
       
        # joint origin positon and rotation
        orig_tag = adom.createElement("origin")
        rpy1 = self.joint_origin_rpy_1 * self.sibling_ind
        rpy = str(rpy1) + " " + str(self.joint_origin_rpy_2) + " " + str(self.joint_origin_rpy_3)
        orig_tag.setAttribute("rpy", rpy)
        xyz = str(self.joint_origin_xyz_1) + " " + str(self.joint_origin_xyz_2) + " " + str(self.joint_origin_xyz_3)
        orig_tag.setAttribute("xyz", xyz)

        # attach all parts to joint
        joint_tag.appendChild(parent_tag)
        joint_tag.appendChild(child_tag)
        joint_tag.appendChild(axis_tag)
        joint_tag.appendChild(limit_tag)
        joint_tag.appendChild(orig_tag)

        # return joint tag
        return joint_tag