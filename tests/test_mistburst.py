import unittest
from firecracker.mistburst import Scene, evaluate, FORMULATIONS, GAS_ONLY

class MistBurstTests(unittest.TestCase):
    def test_three_formulations(self):
        self.assertEqual(set(FORMULATIONS), {"MistBurst-W","MistBurst-G","MistBurst-R"})
    def test_gas_flooding_blocked_for_occupied_rescue(self):
        result=evaluate("co2",Scene(True,True,True,True,True))
        self.assertFalse(result["suppression_authorized"])
        self.assertTrue(any("occupied" in x for x in result["advisory_issues"]))
    def test_chemical_gas_generator_restricted(self):
        result=evaluate("MistBurst-W",Scene(False,True,True,True,True),"chemical_gas_generator")
        self.assertTrue(result["needs_specialist_review"])
        self.assertFalse(result["physical_actuation_enabled"])
    def test_invalid_agent_rejected(self):
        with self.assertRaises(ValueError):
            evaluate("unknown",Scene(False,True,True,True))
    def test_even_clear_gas_review_never_authorizes_release(self):
        result=evaluate("fk5112",Scene(False,True,True,True,True))
        self.assertFalse(result["suppression_authorized"])
        self.assertFalse(result["physical_actuation_enabled"])

if __name__=="__main__": unittest.main()
