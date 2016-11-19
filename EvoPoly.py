from __future__ import division
from pylab import *
import itertools
import copy
#import

nyan = imread('nyan.png')[::20,::20,:3]
#print nyan

class Solution:
	def __init__(self, n_triangles=0):
		self.n_triangles = n_triangles 
		self.triangles = random((self.n_triangles, 3, 2))
		self.colors = random((self.n_triangles, 3))

	def copy(self):
		return copy.deepcopy(self)

	@staticmethod
	def scale(x, a, b):
		x = (b-a)*x + a 

	@staticmethod
	def mutate(x, standard_deviation=1):
		noise = normal(0, standard_deviation, x.shape)
		x += noise
		x[x > 1] = 1
		x[x < 0] = 0

	def triangle_mutate_(self, standard_deviation=.4):
		self.triangles[randint(0, self.triangles.shape[0]), randint(0, 3), randint(0, 2)] += normal(0, standard_deviation)

	def color_mutate_(self, standard_deviation=.4):
		self.colors[randint(0, self.colors.shape[0]), randint(0, 3)] += normal(0, standard_deviation)

	def triangle_mutate(self, standard_deviation=.1):
		Solution.mutate(self.triangles, standard_deviation)

	def color_mutate(self, standard_deviation=.1):
		Solution.mutate(self.colors, standard_deviation)

	@staticmethod
	def breed_attribute(x, y):
#		genes = #doesn't include 2; ugh.
		child = empty(x.shape)
		for g, gene in enumerate(randint(0, 2, x.shape[0])):
			child[g] = x[g] if gene else y[g]
		#child = where(genes, x, y)
		#child = dstack((x, y))[genes]
		return child


	def breed(self, other):
		child = Solution()
		child.triangles = self.breed_attribute(self.triangles, other.triangles)
		child.colors = self.breed_attribute(self.colors, other.colors)
		return child

	def get_pixels(self, n=25):
		pixels = zeros((n,n,3))
		coordinates = dstack(meshgrid(arange(n), arange(n))[::-1])/n
		for triangle, color in zip(self.triangles, self.colors):
			path = matplotlib.path.Path(triangle)
			coordinates.resize(coordinates.size/2, 2)
			mask = path.contains_points(coordinates)
			mask.resize(n, n)
			pixels[mask] = color
		return pixels

	@staticmethod
	def area(t):
		legs = t[0]-t[1], t[0]-t[2]
		return abs(legs[0][0]*legs[1][1]-legs[0][1]*legs[1][0])

	def error_(self, n=25):
		pixel_mismatch = abs(nyan-self.get_pixels (n)).sum()/n**2
		size_penalty = sum(Solution.area(t) for t in self.triangles)/self.triangles.shape[0]
		optimal_size = .1, .02
		size_penalty = 5*(optimal_size[0]-size_penalty)**2 if abs(optimal_size[0]-size_penalty)>optimal_size[1] else 0
		return pixel_mismatch, size_penalty

	def error(self, n=25):
		pixel_mismatch, size_penalty = self.error_(n)
		#print 'er:', pixel_mismatch/size_penalty, pixel_mismatch, size_penalty
		return pixel_mismatch + size_penalty*2

class Evolver:
	def __init__(self, n_solutions=1, n_triangles=1):
		self.solutions = [Solution(n_triangles) for i in range(n_solutions)]
		self.n_solutions = n_solutions
		self.n_triangles = n_triangles

	def sort(self):
		self.solutions.sort(key=lambda x: x.error())
		return self.solutions[0].error_()

	def kill(self, p=.5):#p is the proportion to kill
		del self.solutions[-int(p*len(self.solutions)):]

	def repopulate(self):
		new_solutions = self.n_solutions-len(self.solutions)
		for i in range(new_solutions):
			self.solutions.append(choice(self.solutions).breed(choice(self.solutions)))
		#self.solutions += [Solution(self.n_triangles) for i in range(new_solutions)]

	def mutate_and_select(self):
		for i in range(self.n_solutions):
			solution = self.solutions[i]
			mutated = solution.copy()
			if random() > .5:				
				mutated.color_mutate_()
			else:
				mutated.triangle_mutate_()
			# mutated.triangle_mutate()
			# mutated.color_mutate()
			de = mutated.error() - solution.error()
			if de < 0:# or random() < .1:
				self.solutions[i] = mutated


	def step(self):
		min_error = self.sort()
		print min_error
		self.antistagnate()
		self.kill()
		self.repopulate()
		self.mutate_and_select()
		return min_error

	def antistagnate(self):
		#randomly pick point, find what triangle its in from hash table from error function, add to triangle in front of that
		if all([error==errors[-1] for error in errors[-30:]]):
			print 'antistagnating', 
			mutant = choice(self.solutions[1:])
			gene = randint(0, mutant.triangles.shape[0])
			mutant.triangles[gene] = random((3,2))
			mutant.colors[gene] = random(3)

			# #self.sort()
			# for solution in self.solutions[1:]:
			# 	solution.color_mutate(.05)
			# 	solution.triangle_mutate(.05)






e = Evolver(16, 64)
errors = []

for i in range(1000):
	min_error = e.step()

	errors.append(min_error)
	print i,
#	print sorted(round(s.error(), 4) for s in e.solutions)
errors = array(errors)
plot(errors)
savefig('errors.png')
# imsave('errors.png', p)
e.sort()
pixels = e.solutions[0].get_pixels(1000)
imsave('fig.png', pixels)
import os
os.system('cygstart fig.png')
os.system('cygstart errors.png')
#os.system('cygstart nyan.png')

