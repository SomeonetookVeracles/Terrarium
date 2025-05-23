extends CharacterBody2D

@export var speed := 200.0
@export var ball_path := NodePath("..../Ball") #Set in inspector

func _physics_process(delta):
	var ball = get_node(ball_path)
	var direction = sign(ball.position.y - position.y)
	velocity = Vector2(0, direction * speed)
	move_and_slide()
