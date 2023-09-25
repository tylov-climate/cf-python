import cf
a = cf.read('timeseries.nc')[0]
print(a)
b = a.collapse('minimum')
print(b)
print(b.array)
b = a.collapse('maximum', axes='T')
b = a.collapse('T: maximum')
print(b)
print(b.array)
b = a.collapse('maximum', axes=['X', 'Y'])
b = a.collapse('X: Y: maximum')
print(b)
b = a.collapse('area: maximum')
print(b)
b = a.collapse('T: mean', weights=True)
print(b)
print (b.array)
w = a.weights(True)
print(w)
print(w.array)
b = a.collapse('T: Y: mean', weights='Y')
print(b)
print (b.array)
b = a.collapse('area: mean', weights=True)
print(b)
b = a.collapse('area: mean', weights=a.weights('area'))
print(b)
b = a.collapse('area: mean', weights=True).collapse('T: maximum')
print(b)
print(b.array)
b = a.collapse('area: mean T: maximum', weights=True)
print(b.array)
y = cf.Y(month=12)
y
b = a.collapse('T: maximum', group=y)
print(b)
b = a.collapse('T: maximum', group=6)
print(b)
b = a.collapse('T: maximum', group=cf.djf())
print(b)
c = cf.seasons()
c
b = a.collapse('T: maximum', group=c)
print(b)
b = a.collapse('X: mean', group=cf.Data(180, 'degrees'))
print(b)
b = a.collapse('T: mean within years T: mean over years',
               within_years=cf.seasons(), weights=True)
print(b)
print(b.coordinate('T').bounds.datetime_array)
b = a.collapse('T: minimum within years T: variance over years',
               within_years=cf.seasons(), weights=True)
print(b)
print(b.coordinate('T').bounds.datetime_array)
b = a.collapse('T: mean within years T: mean over years', weights=True,
               within_years=cf.seasons(), over_years=cf.Y(5))
print(b)
print(b.coordinate('T').bounds.datetime_array)
b = a.collapse('T: mean within years T: mean over years', weights=True,
               within_years=cf.seasons(), over_years=cf.year(cf.wi(1963, 1968)))
print(b)
print(b.coordinate('T').bounds.datetime_array)
b = a.collapse('T: standard_deviation within years',
               within_years=cf.seasons(), weights=True)
print(b)
c = b.collapse('T: maximum over years')
print(c)
a = cf.read('timeseries.nc')[0]
print(a)
b = a.cumsum('T')
print(b)
print(a.coordinate('T').bounds[-1].dtarray)
print(b.coordinate('T').bounds[-1].dtarray)
q, t = cf.read('file.nc')
print(q.array)
indices, bins = q.digitize(10, return_bins=True)
print(indices)
print(indices.array)
print(bins.array)
h = cf.histogram(indices)
print(h)
print(h.array)
print(h.coordinate('specific_humidity').bounds.array)
g = q.copy()
g.standard_name = 'air_temperature'
import numpy
g[...] = numpy.random.normal(loc=290, scale=10, size=40).reshape(5, 8)
g.override_units('K', inplace=True)
print(g)
indices_t = g.digitize(5)
h = cf.histogram(indices, indices_t)
print(h)
print(h.array)
h.sum()
q, t = cf.read('file.nc')
print(q.array)
indices = q.digitize(5)
b = q.bin('range', digitized=indices)
print(b)
print(b.array)
print(b.coordinate('specific_humidity').bounds.array)
p, t = cf.read('file2.nc')
print(t)
print(p)
t_indices = t.digitize(4)
p_indices = p.digitize(6)
b = q.bin('mean', digitized=[t_indices, p_indices], weights='area')
print(b)
print(b.array)
q, t = cf.read('file.nc')
print(q)
print(q.array)
p = q.percentile([20, 40, 50, 60, 80])
print(p)
print(p.array)
p80 = q.percentile(80)
print(p80)
g = q.where(q<=p80, cf.masked)
print(g.array)
g.collapse('standard_deviation', weights=True).data
p45 = q.percentile(45, axes='X')
print(p45.array)
g = q.where(q<=p45, cf.masked)
print(g.array)
print(g.collapse('X: mean', weights=True).array)
bins = q.percentile([0, 10, 50, 90, 100], squeeze=True)
print(bins.array)
i = q.digitize(bins, closed_ends=True)
print(i.array)
a = cf.read('air_temperature.nc')[0]
b = cf.read('precipitation_flux.nc')[0]
print(a)
print(b)
c = a.regrids(b, method='conservative')
print(c)
import numpy
domain = cf.Domain.create_regular((0, 360, 5.0), (-90, 90, 2.5))
c = a.regrids(domain, method='linear')
time = cf.DimensionCoordinate.create_regular(
     (0.5, 60.5, 1),
     units=cf.Units("days since 1860-01-01", calendar="360_day"),
     standard_name="time",
     )
time
c = a.regridc([time], axes='T', method='linear')
v = cf.read('vertical.nc')[0]
print(v)
z_p = v.construct('Z')
print(z_p.array)
z_ln_p = z_p.log()
z_ln_p.axis = 'Z'
print(z_ln_p.array)
_ = v.replace_construct('Z', new=z_ln_p)
new_z_p = cf.DimensionCoordinate(data=cf.Data([800, 705, 632, 510, 320.], 'hPa'))
new_z_ln_p = new_z_p.log()
new_z_ln_p.axis = 'Z'
new_v = v.regridc([new_z_ln_p], axes='Z', method='linear')
new_v.replace_construct('Z', new=new_z_p)
print(new_v)
q, t = cf.read('file.nc')
t.data.stats()
x = t + t
x
x.min()
(t - 2).min()
(2 + t).min()
(t * list(range(9))).min()
(t + cf.Data(numpy.arange(20, 29), '0.1 K')).min()
u = t.copy()
u.transpose(inplace=True)
u.Units -= 273.15
u[0]
t + u[0]
t.identities()
u = t * cf.Data(10, 'm s-1')
u.identities()
x = q.dimension_coordinate('X')
x.dump()
(x + x).dump()
(x + 50).dump()
old = cf.bounds_combination_mode('OR')
(x + 50).dump()
x2 = x.copy()
x2.del_bounds()
(x2 + x).dump()
cf.bounds_combination_mode(old)
with cf.bounds_combination_mode('OR'):
   (x2 + x).dump()
import numpy
t = cf.example_field(0)
a = numpy.array(1000)
type(t * a)
type(a + t)
b = numpy.random.randn(t.size).reshape(t.shape)
type(t * b)
type(b * t)
type(t - cf.Data(b))
type(cf.Data(b) * t)
q, t = cf.read('file.nc')
print(q.array)
print(-q.array)
print(abs(-q).array)
q, t = cf.read('file.nc')
print(q.array)
print((q == q).array)
print((q < 0.05).array)
print((q >= q[0]).array)
q.identities()
r = q > q.mean()
r.identities()
y = q.coordinate('Y')
y.identity(strict=True)
del y.standard_name
y.identity(strict=True)
t.min()
u = t.copy()
new_data = t.data - t.data
u.set_data(new_data)
u
u.min()
u[...] = new_data
u.min()
t.data -= t.data
t.min()
q, t = cf.read('file.nc')
lat = q.dimension_coordinate('latitude')
lat.data
sin_lat = lat.sin()
sin_lat.data
d = cf.Data([2, 1.5, 1, 0.5, 0], mask=[1, 0, 0, 0, 1])
e = d.arctanh()
print(e.array)
e.masked_invalid(inplace=True)
print(e.array)
q
q.log()
q.exp()
t
t.log(base=10)
try:
    t.exp()  # Raises Exception
except Exception:
    pass
q, t = cf.read('file.nc')
print(q)
print(q.array)
print(q.coordinate('X').bounds.array)
q.iscyclic('X')
g = q.moving_window('mean', 3, axis='X', weights=True)
print(g)
print(g.array)
print(g.coordinate('X').bounds.array)
print(q)
q.iscyclic('X')
r = q.convolution_filter([0.1, 0.15, 0.5, 0.15, 0.1], axis='X')
print(r)
print(q.dimension_coordinate('X').bounds.array)
print(r.dimension_coordinate('X').bounds.array)
from scipy.signal import windows
exponential_window = windows.exponential(3)
print(exponential_window)
r = q.convolution_filter(exponential_window, axis='Y')
print(r.array)
r = q.derivative('X')
r = q.derivative('Y', one_sided_at_boundary=True)
