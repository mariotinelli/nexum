<?php

declare(strict_types = 1);

namespace App\Actions;

class BcMath
{
    protected string $value = '0';

    protected int $scale = 2;

    public function make(string | int | float $value = 0, int $scale = 2): self
    {
        $self        = new self();
        $self->value = (string) $value;
        $self->scale = $scale;

        return $self;
    }

    public function add(string | int | float $value, ?int $scale = null): self
    {
        $this->value = bcadd($this->value, (string) $value, $scale ?: $this->scale);

        return $this;
    }

    public function sub(string | int | float $value, ?int $scale = null): self
    {
        $this->value = bcsub($this->value, (string) $value, $scale ?: $this->scale);

        return $this;
    }

    public function mul(string | int | float $value, ?int $scale = null): self
    {
        $this->value = bcmul($this->value, (string) $value, $scale ?: $this->scale);

        return $this;
    }

    public function div(string | int | float $value, ?int $scale = null): self
    {
        $this->value = bcdiv($this->value, (string) $value, $scale ?: $this->scale);

        return $this;
    }

    public function percentage(string | int | float $value, ?int $scale = null): self
    {
        $this->value = $this->calculatePercentage($value, $scale);

        return $this;
    }

    public function tax(string | int | float $value, ?int $scale = null): self
    {
        $percentage = $this->calculatePercentage($value, $scale);

        $this->value = bcadd($this->value, $percentage, $scale ?: $this->scale);

        return $this;
    }

    protected function calculatePercentage(string | int | float $value, ?int $scale): string
    {
        $value = $value;

        return bcmul($this->value, (string) ($value / 100), $scale ?: $this->scale);
    }

    public function __toString(): string
    {
        return $this->value;
    }

    public function toFloat(): float
    {
        return (float) $this->value;
    }

    public function toInt(): int
    {
        $powerOfTen = 1;

        for ($i = 0; $i < $this->scale; $i++) {
            $powerOfTen *= 10;
        }

        return (int) bcmul($this->value, (string) $powerOfTen, 0);
    }
}
