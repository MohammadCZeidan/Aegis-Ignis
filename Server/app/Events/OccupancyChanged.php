<?php

namespace App\Events;

use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class OccupancyChanged implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public int $floorId;
    public int $count;
    public float $percentage;

    public function __construct(int $floorId, int $count, float $percentage)
    {
        $this->floorId = $floorId;
        $this->count = $count;
        $this->percentage = $percentage;
    }

    /**
     * Get the channels the event should broadcast on.
     */
    public function broadcastOn(): Channel
    {
        return new Channel('aegis-occupancy');
    }

    /**
     * The event's broadcast name.
     */
    public function broadcastAs(): string
    {
        return 'occupancy.changed';
    }

    /**
     * Get the data to broadcast.
     */
    public function broadcastWith(): array
    {
        return [
            'floor_id' => $this->floorId,
            'count' => $this->count,
            'percentage' => $this->percentage,
            'timestamp' => now()->toISOString(),
        ];
    }
}
