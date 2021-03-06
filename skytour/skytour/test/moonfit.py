x = [
	-2.764193895, -1.961371891, -1.656290164, -1.30732842, -1.158709371, -0.945359755, -0.857407827, -0.7038015981,
	-0.6486940967, -0.5288635476, -0.4942730649, -0.4663968385, -0.3965859287, -0.3755999076, -0.3460053028,
	-0.282238155, -0.2518183324, -0.2077810119, -0.1777473592, -0.1481019359, -0.1197748752, -0.1004889743,
	-0.07517271134, -0.06316613362, -0.04206077453, -0.03500655617, -0.01913548777, -0.01534880664,
	-0.005496277188, -0.003875688084, -0.0005353371809,
]
y = [
	-4.565, -5.339, -5.83, -6.6, -6.983, -7.642, -7.918, -8.484, -8.671,
	-9.165, -9.282, -9.437, -9.72, -9.787, -9.967, -10.213, -10.417, -10.586,
	-10.806, -10.92, -11.154, -11.231, -11.475, -11.528, -11.777, -11.817,
	-12.067, -12.104, -12.346, -12.386, -12.569,
]


N = len(x)
P = sum(x)
Q = sum([z**2 for z in x])
R = sum([z**3 for z in x])
S = sum([z**4 for z in x])
T = sum(y)
U = sum([a*b for a,b in zip(x,y)])
V = sum([a*a*b for a,b in zip(x,y)])
D =  N*Q*S + 2.*P*Q*R - Q**3 - P*P*S - N*R*R
a = (N*Q*V + P*R*T + P*Q*U - Q*Q*T - P*P*V - N*R*U)/D
b = (N*S*U + P*Q*V + Q*R*T - Q*Q*U - P*S*T - N*R*V)/D
c = (Q*S*T + Q*R*U + P*R*V - Q*Q*V - P*S*U - R*R*T)/D

print("{}+x**2 + {}*x + {}".format(a, b, c))

