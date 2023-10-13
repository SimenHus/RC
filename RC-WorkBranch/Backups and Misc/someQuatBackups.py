# Convert sensor readings to y
r = np.arctan2(accRaw[1], accRaw[2])
p = np.arctan2(-accRaw[0], np.sqrt(accRaw[1]**2 + accRaw[2]**2))

#Prev version
magX = magRaw[0]*np.cos(p) + magRaw[1]*np.sin(r) * \
    np.sin(p) + magRaw[2]*np.cos(r)*np.sin(p)
magY = -magRaw[1]*np.cos(r) + magRaw[2]*np.sin(r)
y = np.arctan2(magY, magX)

# https://ahrs.readthedocs.io/en/latest/filters/complementary.html
# magX = magRaw[0]*np.cos(r) + magRaw[1]*np.sin(r) * \
#     np.sin(p) + magRaw[2]*np.sin(r)*np.cos(p)
# magY = magRaw[1]*np.cos(p) - magRaw[2]*np.sin(p)
# y = np.arctan2(-magY, magX)

qMeasured = Quaternion([r, p, y])