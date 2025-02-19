# Dummy classes to simulate a database connection and cursor for testing purposes

class DummyCursor:
    def __init__(self, data):
        """
        Initialize the DummyCursor with the provided data.
        :param data: A list of rows representing dummy table rows.
                     Each row is assumed to be a list where the first element is the place_id.
        """
        self.data = data
        self.params = None

    def execute(self, query, params):
        """
        Simulate executing a SQL query.
        We store the query and parameters. The fetchall() method will use the parameters for filtering.
        :param query: The SQL query string.
        :param params: The query parameters, e.g. a tuple containing a list/tuple of place IDs.
        """
        self.query = query
        self.params = params

    def fetchall(self):
        """
        Return the dummy data, filtered by the provided place_ids (if any).
        We assume that params is a tuple whose first element is the place_ids.
        """
        if self.params:
            place_ids = self.params[0]
            if isinstance(place_ids, (list, tuple)):
                # Filter the data: only include rows where row[0] (place_id) is in the provided list.
                filtered_data = [row for row in self.data if row[0] in place_ids]
                return filtered_data
        return self.data

    def close(self):
        """Simulate closing the cursor."""
        pass


class DummyConnection:
    def __init__(self, dummy_cursor):
        """
        Initialize the DummyConnection with a DummyCursor.
        :param dummy_cursor: An instance of DummyCursor with the dummy data preloaded.
        """
        self._cursor = dummy_cursor

    def cursor(self):
        """Return the dummy cursor (simulated; normally a new cursor would be created)."""
        return self._cursor

    def commit(self):
        """Simulate committing a transaction."""
        pass

    def close(self):
        """Simulate closing the connection."""
        pass