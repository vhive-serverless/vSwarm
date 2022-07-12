package loader

import (
	"github.com/ease-lab/vSwarm/tools/trace-plotter/models"
)

type Loader interface {
	GetTraces(pageSize int, traces *[]models.Trace)
}
