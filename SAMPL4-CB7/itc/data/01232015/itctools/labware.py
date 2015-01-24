class Labware(object):

    def __init__(self, RackLabel, RackType, RackID=None):
        """
        Define basic Tecan labware.

        Parameters
        ----------
        RackLabel : str
           Tecan labware name on deck (e.g. 'SourcePlate', 'Buffer', 'Water')
        RackType : str
           Tecan labeware type (e.g. 'Trough 100ml', 'ITC Plate')
        RackID : str, optional
           Tecan barcode.

        """
        self.RackLabel = RackLabel
        self.RackType = RackType
        self.RackID = RackID


class PipettingLocation(object):

    def __init__(self, RackLabel, RackType, Position):
        # Information for Tecan LiHa.
        self.RackLabel = RackLabel
        self.RackType = RackType
        self.Position = Position
