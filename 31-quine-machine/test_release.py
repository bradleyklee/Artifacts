"""Regression tests: independent clock, lambda update, Scott dispatcher, export."""
import unittest
from lambda_runtime import *
from release import TAGS, DISPATCH, decode_tag, eval_step, pair_values

class ReleaseChecks(unittest.TestCase):
    def test_literal_quine_cycle(self):
        q=Q; states=[]
        for i in range(6):
            states.append(q)
            path=next(iter(redexes(q)),None)
            self.assertIsNotNone(path)
            q=beta(q,path)
        self.assertEqual(q,Q)
        self.assertEqual(len(set(states)),6)

    def test_ten_cycles_with_real_export(self):
        q=TAGS[0]; p=pair(N(0),N(1)); reference=(0,1)
        costs=[]
        for cycle in range(10):
            for i in range(6):
                result,n,events=eval_step(app(DISPATCH,q,p),track_export=True)
                q,_=normalize(app(FST,result));p,_=normalize(app(SND,result))
                self.assertEqual(decode_tag(q),(i+1)%6)
                costs.append(n)
                if i==2: reference=reference[1],sum(reference)
                if i==4:
                    self.assertEqual(len(events),1)
                    self.assertEqual(pair_values(events[0][2]),reference)
                self.assertEqual(pair_values(p),reference)
        self.assertEqual(costs[6:12],[11,11,23,11,12,11])

if __name__=='__main__':unittest.main()
