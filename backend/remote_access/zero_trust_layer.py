"""
Zero Trust Layer - Placeholder
"""

class ZeroTrustLayer:
    def __init__(self):
        self.enabled = False
    
    async def verify(self, request):
        return True

zero_trust_layer = ZeroTrustLayer()
