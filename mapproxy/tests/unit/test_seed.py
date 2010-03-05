from functools import partial
from cStringIO import StringIO
from mapproxy.core.cache import Cache, CacheManager
from mapproxy.wms.layer import VLayer, WMSCacheLayer
from mapproxy.core.grid import TileGrid
from mapproxy.core.seed import TileSeeder, TileProgressMeter
from mapproxy.tests.helper import Mocker
from mocker import ANY

class TestTileSeeder(Mocker):
    def setup(self):
        Mocker.setup(self)
        self.cache_mgr = self.mock(CacheManager)
        self.grid = TileGrid(epsg=4326, is_geodetic=True)
        self.cache = Cache(self.cache_mgr, self.grid)
        self.layers = VLayer({}, [WMSCacheLayer(self.cache)])
        self.dummy_out = StringIO()
        progress_meter = partial(TileProgressMeter, out=self.dummy_out)
        self.seeder = TileSeeder(self.layers, progress_meter)
    def test_seed_location(self):
        self.cache_mgr.expire_timestamp = ANY
        self.mocker.count(1, None)
        self.expect(self.cache_mgr.load_tile_coords([(0, 0, 0)]))
        self.expect(self.cache_mgr.load_tile_coords([(1, 0, 1)]))
        self.expect(self.cache_mgr.load_tile_coords([(2, 1, 2)]))
        self.expect(self.cache_mgr.load_tile_coords([(4, 3, 3)]))
        self.expect(self.cache_mgr.load_tile_coords([(8, 6, 4)]))
        self.replay()
        
        self.seeder.add_seed_location((8, 53), res=0.1, px_buffer=0)
        self.seeder.seed()
        self.dummy_out.seek(0)
        assert self.dummy_out.readline().startswith('start seeding #0: ')
    def test_seed_level(self):
        self.cache_mgr.expire_timestamp = ANY
        self.mocker.count(1, None)
        self.expect(self.cache_mgr.load_tile_coords([(0, 0, 0)]))
        self.expect(self.cache_mgr.load_tile_coords([(1, 0, 1)]))
        self.expect(self.cache_mgr.load_tile_coords([(2, 1, 2)]))
        self.expect(self.cache_mgr.load_tile_coords([(4, 2, 3)]))
        self.replay()
        self.seeder.add_seed_location((0, 0, 30, 15), level=3, px_buffer=0)
        self.seeder.seed()
        
        