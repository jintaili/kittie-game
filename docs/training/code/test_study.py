import unittest
from analysis import fisher,matched,wilson,newcombe
from timing import Timing,SingleRequest
class AnalysisTest(unittest.TestCase):
 def test_fixed_counts(self):
  self.assertAlmostEqual(fisher(47,50,39,50),.04071468493453525)
  self.assertAlmostEqual(fisher(39,50,47,50),fisher(47,50,39,50))
  self.assertAlmostEqual(fisher(50,50,47,50),.24242424242424243)
  self.assertAlmostEqual(wilson(39,50)[0],.6475845041874634)
  self.assertGreater(newcombe(47,50,39,50)[0],0)
 def test_pairing_rejects_duplicates_and_unmatched_entries(self):
  a=[{'scenario':0,'win':True,'entry_sha256':'a'}]
  with self.assertRaises(ValueError):matched(a+a,a)
  with self.assertRaises(ValueError):matched(a,[{**a[0],'entry_sha256':'b'}])
  with self.assertRaises(ValueError):matched(a,[{**a[0],'scenario':1}])
class TimingTest(unittest.TestCase):
 def test_measured_single_outstanding_and_interval(self):
  c=SingleRequest(Timing());c.observe(0)
  with self.assertRaises(ValueError):c.observe(1)
  c.reply(18);self.assertTrue(c.ready(18));c.apply(18)
  with self.assertRaises(ValueError):c.observe(23)
  c.observe(24);self.assertEqual(c.requests,2)
 def test_floor_early_late_and_terminal(self):
  c=SingleRequest(Timing(6,'floor',(20,20,20)));c.observe(0);c.reply(10)
  self.assertFalse(c.ready(19));self.assertTrue(c.ready(20));c.apply(20)
  c.observe(26);c.reply(50);self.assertTrue(c.ready(50));c.apply(50)
  c.observe(56);c.finish();c.reply(70);self.assertFalse(c.ready(100))
  with self.assertRaises(ValueError):c.apply(100)
 def test_one_frame_and_no_implicit_delay_reuse(self):
  c=SingleRequest(Timing(1,'floor',(18,)));c.observe(0);c.reply(15);c.apply(18)
  self.assertEqual(c.next_observation,19)
  with self.assertRaises(ValueError):c.observe(19)
if __name__=='__main__':unittest.main()
