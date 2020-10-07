# From PurpleAir API docs
# Transcribed to Python
class PurpleAir:
	def calcAQI(self, Cp, Ih, Il, BPh, BPl):
		a = (Ih - Il)
		b = (BPh - BPl)
		c = (Cp - BPl)
		return round((a/b) * c + Il)
		      
	def aqFromPM(self, pm):
		if (pm > 350.5):
		  return self.calcAQI(pm, 500, 401, 500, 350.5)
		elif (pm > 250.5):
		  return self.calcAQI(pm, 400, 301, 350.4, 250.5)
		elif (pm > 150.5):
		  return self.calcAQI(pm, 300, 201, 250.4, 150.5)
		elif (pm > 65):
			return self.calcAQI(pm, 200, 151, 150.4, 55.5)
		elif (pm >= 0):
			# LRAPA PM2.5 (µg/m³) = 0.5 x PA (PM2.5 CF=ATM) – 0.66
			return round(.5 * pm - .66)
		else:
		  return -1