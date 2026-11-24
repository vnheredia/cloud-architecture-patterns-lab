import unittest
from labs.simulations import run_lab

class SimulationSmokeTests(unittest.TestCase):
    def test_all_labs_return_expected_shape(self):
        for lab_id in range(1, 9):
            with self.subTest(lab=lab_id):
                result = run_lab(lab_id, {})
                self.assertIn('summary', result)
                self.assertIn('status', result)
                self.assertIn('metrics', result)
                self.assertIsInstance(result['logs'], list)
                self.assertGreater(len(result['logs']), 0)

    def test_circuit_breaker_stays_open_after_failed_probe(self):
        result = run_lab(1, {'failure_threshold': 2, 'probe_success': 'false'})
        self.assertEqual(result['status'], 'OPEN')

    def test_retry_stops_at_attempt_limit(self):
        result = run_lab(2, {'failures_before_success': 5, 'max_attempts': 2})
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['metrics']['attempts'], 2)

    def test_timeout_counts_requests_over_deadline(self):
        result = run_lab(3, {'timeout_ms': 500, 'fast_response_ms': 800, 'slow_response_ms': 3500})
        self.assertEqual(result['metrics']['timed_out'], 2)

    def test_round_robin_distribution(self):
        result = run_lab(5, {'request_count': 10, 'backend_count': 3})
        self.assertEqual([item['requests'] for item in result['details']], [4, 3, 3])

    def test_hub_route_can_be_restricted(self):
        result = run_lab(6, {'spoke_count': 2, 'allow_spoke_to_spoke': 'false'})
        self.assertEqual(result['status'], 'RESTRICTED')

    def test_migration_validation_failure_returns_rollback(self):
        result = run_lab(7, {'server_count': 5, 'validation_pass': 'false'})
        self.assertEqual(result['status'], 'ROLLBACK')

    def test_bastion_rejects_unauthorized_user(self):
        result = run_lab(8, {'admin_authorized': 'false', 'direct_access': 'true'})
        self.assertEqual(result['status'], 'ACCESS DENIED')

    def test_invalid_lab_id_raises(self):
        with self.assertRaises(ValueError):
            run_lab(99, {})

if __name__ == '__main__':
    unittest.main()
