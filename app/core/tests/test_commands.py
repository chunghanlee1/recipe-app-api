# allow us to mock behavior of django get database function.
# simulate behavior when database is available and not
# when we run our command
from unittest.mock import patch 
# allow us to call the command in the source code
from django.core.management import call_command
# Error that django will throw when db is not available
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """Test waiting for db when db is available"""
        # whenever the __getitem__ method is called in the block, 
        # the code mocks/overrides the default connection handler 
        # and replace it with a mock object that returns what we want
        # and monitors the number of calls being made to it
        with patch('django.db.utils.ConnectionHandler.__getitem__') as get_item:
            # instruct this mock to always return true
            get_item.return_value=True
            # wait_for_db is the command we will create
            call_command('wait_for_db')
            # access the call_count attribute for the object
            self.assertEqual(get_item.call_count,1)

        # Use patch as decorator. Essentially does the same thing as above,
        # overriding the default bahavor of a function. The mock object
        # will then be passed into the function we define below.
        # Here it's the time_sleep object that's analogous
        # to get_item above. We patch time.sleep function
        # in order to save time here
        @patch('time.sleep', return_value=True)
        def test_wait_for_db(self, time_sleep):
            """Test waiting for db until the db is ready"""
            with patch('django.db.utils.ConnectionHandler.__getitem__') as get_item:
                # Make the __getitem__ method return Error the first five times
                get_item.side_effect=[OperationalError]*5 +[True]
                call_command('wait_for_db')
                self.assertEqual(get_item.call_count,6)