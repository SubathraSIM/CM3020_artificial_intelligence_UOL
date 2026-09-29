# import required library
import unittest
import creature
import pybullet as p

class TestCreature(unittest.TestCase):
    # checks creature class have
    def testCreatExists(self):
        self.assertIsNotNone(creature.Creature)

    # get_flat_links return the correct number of links
    def testCreatureGetFlatLinks(self):
        c = creature.Creature(gene_count=4)
        links = c.get_flat_links()
        self.assertEqual(len(links), 4)

    # expanded links is not smaller than flat links
    def testExpLinks(self):
        c = creature.Creature(gene_count=25)
        links = c.get_flat_links()
        exp_links = c.get_expanded_links()
        self.assertGreaterEqual(len(exp_links), len(links))

    # to_xml return a urdf xml string
    def testToXMLNotNone(self):
        c = creature.Creature(gene_count=2)
        xml_str = c.to_xml()
        self.assertIsNotNone(xml_str)

    # generated urdf can be loaded by pybullet
    def testLoadXML(self):
        c = creature.Creature(gene_count=20)
        xml_str = c.to_xml()
        with open('test.urdf', 'w') as f:
            f.write(xml_str)
        p.connect(p.DIRECT)
        cid = p.loadURDF('test.urdf')
        self.assertIsNotNone(cid)

    # motor object can create or not
    def testMotor(self):
        m = creature.Motor(0.1, 0.5, 0.5)
        self.assertIsNotNone(m)

    # check that motor output is correct
    def testMotorVal(self):
        m = creature.Motor(0.1, 0.5, 0.5)
        # edited by me initial value was 1 I changed it to be 0.5
        self.assertEqual(m.get_output(), 0.5)

    # check motor output positive after multiple steps
    def testMotorVal2(self):
        m = creature.Motor(0.6, 0.5, 0.5)
        m.get_output()
        m.get_output()     
        self.assertGreater(m.get_output(), 0)
    
    # checks distance travelled increases after the creature move
    def testDist(self):
        c = creature.Creature(3)
        c.update_position((0, 0, 0))
        d1 = c.get_distance_travelled()
        c.update_position((1, 1, 1))
        d2 = c.get_distance_travelled()
        self.assertGreater(d2, d1)
        

unittest.main()